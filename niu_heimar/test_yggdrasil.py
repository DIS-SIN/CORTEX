import sys

from confluent_kafka import avro
from confluent_kafka import KafkaError

from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError


VALUE_SCHEMA_STR = """
{
    "namespace": "Yggdrasil",
	"name": "Poem",
	"type": "record",
	"fields": [
		{"name": "name", "type": "string"},
		{"name": "text",  "type": "string"}
	]
}
"""
VALUE_SCHEMA = avro.loads(VALUE_SCHEMA_STR)

TEST_MESSAGES = [
    {"name": "Völuspá", "text": "An ash I know there stands, Yggdrasill is its name, a tall tree, showered with shining loam. From there come the dews that drop in the valleys. It stands forever green over Urðr's well."},
    {"name": "Hávamál", "text": "I know that I hung on a windy tree nine long nights, wounded with a spear, dedicated to Odin, myself to myself, on that tree of which no man knows from where its roots run"},
]


def produce_test_messages(broker, schema_registry, schema, topic):
    producer = AvroProducer(
        {
            'bootstrap.servers': broker,
            'schema.registry.url': schema_registry
        },
        default_value_schema=schema
    )

    for message in TEST_MESSAGES:
        producer.produce(topic=topic, value=message)
        print('Produced [%s]' % message)
    producer.flush()


def consume_test_messages(broker, schema_registry, topic):
    consumer = AvroConsumer({
        'bootstrap.servers': broker,
        'group.id': 'groupid',
        'schema.registry.url': schema_registry,
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe([topic])

    count = 0
    while True:
        try:
            msg = consumer.poll(1)

        except SerializerError as e:
            print("Message deserialization failed for {}: {}".format(msg, e))
            break

        if msg is None:
            count += 1
            if count == 10:
                break
            continue

        if msg.error():
            print("AvroConsumer error: {}".format(msg.error()))
            continue

        print('Consumed', msg.value())

    consumer.close()


if __name__ == "__main__":

    if len(sys.argv) < 4:
        print("Usage: python3 producer.py <broker> <schema_registry> <topic>")
        exit(1)

    BROKER_HOST = sys.argv[1]
    SCHEMA_REGISTRY = sys.argv[2]
    TOPIC = sys.argv[3]

    produce_test_messages(BROKER_HOST, SCHEMA_REGISTRY, VALUE_SCHEMA, TOPIC)
    consume_test_messages(BROKER_HOST, SCHEMA_REGISTRY, TOPIC)
