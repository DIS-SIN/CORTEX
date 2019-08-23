import json
import sys

from confluent_kafka import avro, Consumer
from confluent_kafka import KafkaError, KafkaException

from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError


def produce_message(context, topic, uid, text):
    producer = AvroProducer(
        {
            'bootstrap.servers': context.broker_url,
            'schema.registry.url': context.schema_registry_url
        },
        default_value_schema=context.player_schema
    )
    producer.produce(topic=topic, value={"uid": uid, "content": text})
    producer.flush()


def consume_avro_messages(context, topic):
    consumer = AvroConsumer({
        'bootstrap.servers': context.broker_url,
        'group.id': 'group_id_1',
        'schema.registry.url': context.schema_registry_url,
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
            print("No message")
            continue

        if msg.error():
            print("AvroConsumer error: {}".format(msg.error()))
            continue

    print(msg)
    consumer.close()
    return msg


def consume_messages(context, group_id, topic, uid):
    consumer = Consumer({
        'bootstrap.servers': context.broker_url,
        'group.id': group_id,
        'session.timeout.ms': 6000,
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe([topic])
    messages = []

    # Read messages from Kafka, print to stdout
    count = 0
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                print("No message")
                count += 1
                if count == 5:
                    return False
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Proper message
                sys.stderr.write('%% %s [%d] at offset %d with key %s:\n' %
                                 (msg.topic(), msg.partition(), msg.offset(),
                                  str(msg.key())))
                if msg.topic() != topic:
                    print('Wrong topic %s' % msg.topic())
                    count += 1
                    continue

                msg_str = msg.value().decode()
                print('msg_str', msg_str)

                json_obj = json.loads(msg_str)
                if 'payload' in json_obj:
                    payload = json_obj['payload']
                    print('payload', payload)
                    if 'uid' in payload and payload['uid'].startswith(uid):
                        return True
                    if 'data' in payload:
                        for item in payload['data']:
                            if item['uid'].startswith(uid):
                                return True

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
    return False
