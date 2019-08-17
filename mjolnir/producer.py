import sys
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from config_handler import ConfigHandler
from profiler import profile, print_profile_statistics


@profile
def produce_messages(input_file, prefixed_topic, producer):
    lines = [line.strip('\n') for line in input_file.readlines()]
    headers = lines[0].split('\t')
    count = 0
    for line in lines[1:]:
        values = line.split('\t')
        message = {headers[i]: values[i] for i in range(0, len(values))}
        count += 1
        producer.produce(topic=prefixed_topic, value=message)
        if count % 1000 == 0:
            print('.', end='', flush=True)
            producer.flush()
    producer.flush()
    print('. %s' % count)


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage: python producer.py <config> <tsv_dir>")
        exit(1)

    handler = ConfigHandler(sys.argv[1])
    tsv_dir = sys.argv[2]

    config = handler.get_eval_option('yggdrasil', 'conf')
    prefix = handler.get_config_option('info', 'prefix')

    broker = config['broker']
    schema_registry = config['schema_registry']

    schema = handler.get_config_option('avro', 'schema')
    avro_schema = avro.loads(schema)
    avro_producer = AvroProducer(
        {
            'bootstrap.servers': broker,
            'schema.registry.url': schema_registry
        },
        default_value_schema=avro_schema
    )

    entity_topics = [
        k for k, _ in handler.get_eval_option('jotunheimr', 'topics').items()
        if '_TO_' not in k
    ]

    relation_topics = [
        k for k, _ in handler.get_eval_option('jotunheimr', 'topics').items()
        if '_TO_' in k
    ]

    for topic in entity_topics + relation_topics:
        file_name = '%s/%s.tsv' % (tsv_dir, topic)
        with open(file_name, mode='rt', encoding='utf-8') as text_file:
            prefixed_topic = "%s_%s" % (prefix, topic)
            print('\nProcess [%s] to [%s] topic ' % (file_name, prefixed_topic))
            produce_messages(text_file, prefixed_topic, avro_producer)

    print_profile_statistics()
