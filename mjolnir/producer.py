import sys
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from config_handler import ConfigHandler

def produce_messages(input_file, producer):
    lines = [line.strip('\n') for line in input_file.readlines()]
    headers = lines[0].split('\t')
    count = 0
    for line in lines[1:]:
        values = line.split('\t')
        message = {headers[i]: values[i] for i in range(0, len(values))}
        print(message)
        count += 1
        if count == 10:
            break
        avroProducer.produce(topic=topic, value=message)
    avroProducer.flush()


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage: python producer.py <config> <tsv_dir>")
        exit(1)

    handler = ConfigHandler(sys.argv[1])
    tsv_dir = sys.argv[2]

    broker = '%s:%s' % (
        handler.get_config_option('yggdrasil', 'broker_host'),
        handler.get_config_option('yggdrasil', 'broker_port'),
    )
    schema_registry = '%s:%s' % (
        handler.get_config_option('yggdrasil', 'schema_registry_host'),
        handler.get_config_option('yggdrasil', 'schema_registry_port'),
    )
    
    avro_schema = avro.loads(handler.get_config_option('avro', 'def'))
    avro_producer = AvroProducer(
        {
            'bootstrap.servers': broker,
            'schema.registry.url': schema_registry
        },
        default_value_schema=avro_schema
    )

    topics = [
        k for k, _ in handler.get_eval_option('jotunheimr', 'topics').items()
    ]

    for topic in topics:
        file_name = '%s/%s.tsv' % (tsv_dir, topic)
        with open(file_name, mode='rt', encoding='utf-8') as text_file:
            produce_messages(text_file, None)
