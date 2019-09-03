import json
import time
import sys

from confluent_kafka import avro, Consumer
from confluent_kafka import KafkaError, KafkaException
from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro.serializer import SerializerError

from hash_util import get_md5


def produce_player_messages(context, topic, responses):
    producer = AvroProducer(
        {
            'bootstrap.servers': context.broker,
            'schema.registry.url': context.schema_registry_url
        },
        default_value_schema=context.response_schema
    )

    count = 0
    for response in responses:
        text = json.dumps(response)
        producer.produce(topic=topic, value={"uid": get_md5(text), "content": text})
        count += 1
        if count % 100 == 0:
            producer.flush()

    producer.flush()


def produce_asgard_message(context, topic, sentiment_message):
    producer = AvroProducer(
        {
            'bootstrap.servers': context.broker,
            'schema.registry.url': context.schema_registry_url
        },
        default_value_schema=context.sentiment_schema
    )
    producer.produce(topic=topic, value=sentiment_message)
    producer.flush()


def consume_json_message(context, group_id, topics, timeout=5, max_messages=1):
    consumer = Consumer({
        'bootstrap.servers': context.broker,
        'group.id': '%s-%s' % (group_id, time.time()),
        'session.timeout.ms': 6000,
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe(topics)
    messages = []

    count = 0
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                print("No message")
                count += 1
                if count == timeout:
                    break
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                print('%s [%d] at offset %d with key %s:\n' % (
                    msg.topic(), msg.partition(), msg.offset(), str(msg.key()))
                )
                print(msg.value())
                json_msg = json.loads(msg.value().decode())
                if 'payload' in json_msg:
                    messages.append(json_msg['payload'])
                else:
                    messages.append(json_msg)
                if len(messages) == max_messages:
                    break

    except KeyboardInterrupt:
        print('Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

    if max_messages == 1 and len(messages) == 1:
        return messages[0]
    return messages
