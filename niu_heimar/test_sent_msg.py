import sys

from confluent_kafka import avro
from confluent_kafka import KafkaError

from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError


VALUE_SCHEMA_STR = """
{
    "namespace": "cortex.streamprocessors.asgard",
    "type": "record",
    "name": "OutputData",
    "doc": "This schema is used to serialize processed data by asgard",
    "fields": [
        {"name": "uid", "type": ["string", "long"]},
        {"name": "data", "type": {
                "name": "processedText",
                "type": "array",
                "items": {
                    "name": "providersProcessedText",
                    "type": "array",
                    "items": {
                        "name": "processedTextProvider",
                        "type": "record",
                        "fields": [
                            { "name": "uid", "type": ["string", "null"]},
                            { "name": "text", "type": "string"},
                            { "name": "language", "type": "string"},
                            { "name": "sentimentScore", "type": "double"},
                            { "name": "magnitudeScore", "type": "double" },
                            { "name": "provider", "type": "string"},
                            { "name": "sentences", "type": {
                                    "name": "processedSentences",
                                    "type": "array",
                                    "items": {
                                        "name": "processedSentence",
                                        "type": "record",
                                        "fields": [
                                            {"name": "text", "type": "string"},
                                            {"name": "sentimentScore", "type": "double"},
                                            {"name": "magnitudeScore", "type": "double"}
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    ]
}
"""
VALUE_SCHEMA = avro.loads(VALUE_SCHEMA_STR)


def consume_test_messages(broker, schema_registry, topic):
    consumer = AvroConsumer({
        'bootstrap.servers': broker,
        'group.id': 'groupid',
        'schema.registry.url': schema_registry,
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
            print('-')
            count += 1
            if count == 60:
                break
            continue

        if msg.error():
            print("AvroConsumer error: {}".format(msg.error()))
            continue

        print(msg.value())

    consumer.close()


if __name__ == "__main__":

    if len(sys.argv) < 4:
        print("Usage: python3 producer.py <broker> <schema_registry> <topic>")
        exit(1)

    BROKER_HOST = sys.argv[1]
    SCHEMA_REGISTRY = sys.argv[2]
    TOPIC = sys.argv[3]

    consume_test_messages(BROKER_HOST, SCHEMA_REGISTRY, TOPIC)
