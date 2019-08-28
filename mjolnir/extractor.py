import sys
from config_handler import ConfigHandler

U_CONST = 'CREATE CONSTRAINT ON (n:%s) ASSERT n.%s IS UNIQUE'
P_CONST = 'CREATE INDEX ON :%s(point)'
I_CONST = 'CREATE INDEX ON :%s(%s)'
TOPIC_PREFIX = "neo4j.topic.cypher"
SINK_CONFIG = """
{
  "name": "Neo4jSinkConnector",
  "config": {
    "topics": "%s",
    "connector.class": "streams.kafka.connect.sink.Neo4jSinkConnector",
    "errors.retry.timeout": "-1",
    "errors.retry.delay.max.ms": "1000",
    "errors.tolerance": "all",
    "errors.log.enable": true,
    "errors.log.include.messages": true,
    "neo4j.server.uri": "bolt://%s",
    "neo4j.authentication.basic.username": "%s",
    "neo4j.authentication.basic.password": "%s",
    "neo4j.encryption.enabled": false,
    %s
  }
}
"""
APOC_SCHEMA_ASSERT = "CALL apoc.schema.assert({%s},{%s});"


def load_lines(file_name):
    with open(file_name, mode='rt', encoding='utf-8') as text_file:
        lines = [line.strip('\n') for line in text_file.readlines()]
        return lines

def create_rows(lines, row_info_list):
    rows = set()
    for line in lines:
        row = ''
        count = 0
        for row_info in row_info_list:
            _, start_index, end_index = row_info
            row += line[start_index:start_index+end_index].strip()
            count += 1
            if count < len(row_info_list):
                row += '\t'
        rows.add(row)
    return sorted(rows)


def write_rows(rows, file_name, row_info_list):
    headers = [e[0] for e in row_info_list]
    with open(file_name, mode='wt', encoding='utf-8') as text_file:
        text_file.write('\t'.join(headers) + '\n')
        for item in rows:
            text_file.write(item + '\n')
    return len(rows)


def create_contraints(file_name, cons_conf):
    with open(file_name, mode='wt', encoding='utf-8') as text_file:
        count = 0
        const_str, index_str = [], []
        for name, info in cons_conf.items():
            cons, ind_l, con_l = [], set(), set()
            if 'p' in info:
                cons.append(P_CONST % name)
                ind_l.add('point')
            if 'u' in info:
                cons.append(U_CONST % (name, info['u']))
                con_l.add(info['u'])
            if 'i' in info:
                for entity_prop in info['i']:
                    cons.append(I_CONST % (name, entity_prop))
                    ind_l.add(entity_prop)
            if 'c' in info:
                cons.append(I_CONST % (name, ','.join(info['c'])))
                ind_l.update(set(info['c']))
            if cons:
                for con in cons:
                    text_file.write('%s;\n' % con)
                    count += 1
            if con_l:
                const_str.append('%s:[%s]' % (name, ','.join(["'%s'" % c for c in sorted(con_l)])))
            if ind_l:
                index_str.append('%s:[%s]' % (name, ','.join(["'%s'" % c for c in sorted(ind_l)])))
        text_file.write('CALL db.constraints();\n')
        text_file.write('CALL db.indexes();\n')
        text_file.write('CALL db.awaitIndexes();\n')
        print('%s constraints and indexes created.' % count)

        schema_statement = APOC_SCHEMA_ASSERT % (
            ','.join(index_str), ','.join(const_str)
        )
        return schema_statement


def create_sink_config(file_name, host_conf, topics_conf, prefix, statement):
    with open(file_name, mode='wt', encoding='utf-8') as text_file:
        topic_list = ','.join(
            ['%s_%s' % (prefix, k) for k, _ in topics_conf.items()] +
            ['%s_constraints' % prefix]
        )
        topics = ',\n    '.join(
            [
                '"%s.%s_%s": "%s"' % (TOPIC_PREFIX, prefix, k, v)
                for k, v in topics_conf.items()
            ] +
            [
                '"%s.%s_constraints": "%s"' % (TOPIC_PREFIX, prefix, statement)
            ]
        )
        text_file.write(SINK_CONFIG % (
            topic_list,
            host_conf['host'], host_conf['username'], host_conf['password'],
            topics
        ))
        print('%s topics created.' % len(topics_conf))


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('python extractor.py <config> <source_dir> <target_dir>\n')
        exit(1)

    source_dir = sys.argv[2]
    target_dir = sys.argv[3]
    config_handler = ConfigHandler(sys.argv[1])
    prefix = config_handler.get_config_option('info', 'prefix')

    sources = config_handler.get_eval_option('extraction', 'sources')
    for source in sources:
        tsv_files = source['tsv_files']

        for tsv_file in tsv_files:
            file_name = '%s/%s' % (source_dir, tsv_file['file_name'])
            lines = load_lines(file_name)

            ent_conf = tsv_file['entities']
            for entity_name, entity_info in ent_conf.items():
                file_name = '%s/%s.tsv' % (target_dir, entity_name)
                rows = create_rows(lines, entity_info)
                count = write_rows(rows, file_name, entity_info)
                print('%s [%s] entities extracted.' % (count, entity_name))

            rel_conf = tsv_file['relations']
            for relation_name, relation_info in rel_conf.items():
                file_name = '%s/%s.tsv' % (target_dir, relation_name)
                rows = create_rows(lines, relation_info)
                count = write_rows(rows, file_name, relation_info)
                print('%s [%s] relations extracted.' % (count, relation_name))

    con_conf = config_handler.get_eval_option('jotunheimr', 'constraints')
    file_name = '%s/schema_for_jotunheimr.cql' % target_dir
    schema_statement = create_contraints(file_name, con_conf, )

    crd_conf = config_handler.get_eval_option('jotunheimr', 'credentials')
    tpc_conf = config_handler.get_eval_option('jotunheimr', 'topics')
    file_name = '%s/jotunheimr_sink.json' % target_dir
    create_sink_config(file_name, crd_conf, tpc_conf, prefix, schema_statement)
