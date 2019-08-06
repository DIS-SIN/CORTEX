import sys
from config_handler import ConfigHandler

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


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('python extractor.py <instructions> <input_file> <output_dir>\n')
        exit(1)

    print('python extractor.py', *sys.argv[1:])
    config_handler = ConfigHandler(sys.argv[1])
    lines = load_lines(sys.argv[2])
    output_dir = sys.argv[3]

    ent_list_config = config_handler.get_eval_option('entity_list', 'conf')
    ent_config_dict = {
        k: config_handler.get_eval_option('entity_info', v)
        for k, v in ent_list_config.items()
    }
    for entity_name, entity_info in ent_config_dict.items():
        file_name = '%s/%s.tsv' % (output_dir, entity_name)
        rows = create_rows(lines, entity_info)
        count = write_rows(rows, file_name, entity_info)
        print('%s [%s] entities extracted.' % (count, entity_name))

    rel_list_config = config_handler.get_eval_option('relation_list', 'conf')
    rel_config_dict = {
        k: config_handler.get_eval_option('relation_info', v)
        for k, v in rel_list_config.items()
    }
    for relation_name, relation_info in rel_config_dict.items():
        file_name = '%s/%s.tsv' % (output_dir, relation_name)
        rows = create_rows(lines, relation_info)
        count = write_rows(rows, file_name, relation_info)
        print('%s [%s] relations extracted.' % (count, relation_name))
