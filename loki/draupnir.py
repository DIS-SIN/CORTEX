import hashlib
import json
from time import sleep
import sys

from confluent_kafka import avro, Consumer
from confluent_kafka import KafkaError, KafkaException

from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError


SURVEY_VALUE_SCHEMA_STR = """
{
    "namespace": "CORTEX",
    "name": "Survey",
    "type": "record",
    "fields": [
        {"name": "uid", "type": "string"},
        {"name": "format", "type": "string"},
        {"name": "content", "type": "string"}
    ]
}
"""
SURVEY_VALUE_SCHEMA = avro.loads(SURVEY_VALUE_SCHEMA_STR)


RESPONSE_VALUE_SCHEMA_STR = """
{
    "namespace": "CORTEX",
    "name": "Response",
    "type": "record",
    "fields": [
        {"name": "uid", "type": "string"},
        {"name": "content", "type": "string"}
    ]
}
"""

RESPONSE_VALUE_SCHEMA = avro.loads(RESPONSE_VALUE_SCHEMA_STR)

SURVEYS = {
    'TEST_SUR': {
        'survey_evalese': 'data/TEST_SUR_evalese.json',
        'survey_template': 'data/TEST_SUR_template.json',
        'survey_response': 'data/TEST_SUR_responses.json',
    },
    'ELDP': {
        'survey_evalese': 'data/ELDP_evalese.json',
        'survey_template': 'data/ELDP_template.json',
        'survey_response': 'data/ELDP_responses.json',
    },
}


def write_rows(messages):
    for topic, message_list in messages.items():
        with open('data/%s.json' % topic, mode='wt', encoding='utf-8') as t_file:
            json.dump(message_list, t_file, ensure_ascii=False)
            print('[%s] written %s rows.' % (topic, len(message_list)))


def get_md5(text):
    m = hashlib.md5()
    m.update(text.encode())
    return m.hexdigest()


def get_content(file_name):
    text = ''
    with open(file_name, mode='rt', encoding='utf-8') as text_file:
        for line in text_file.readlines():
            text += line
    return text


def produce_messages(designer_producer, player_producer):

    for survey_uid, survey_dict in SURVEYS.items():
        print('---------- Survey [%s] ----------' % survey_uid)

        designer_producer.produce(
            topic='survey_evalese',
            value={
                "uid": survey_uid,
                "format": "evalese",
                "content": get_content(survey_dict['survey_evalese'])
            }
        )
        print('E', end='', flush=True)

        designer_producer.produce(
            topic='survey_json',
            value={
                "uid": survey_uid,
                "format": "template",
                "content": get_content(survey_dict['survey_template'])
            }
        )
        print('T', end='', flush=True)
        designer_producer.flush()

        responses = json.loads(get_content(survey_dict['survey_response']))
        count = 0
        for response in responses:
            text = json.dumps(response)
            player_producer.produce(
                topic='survey_response',
                value={
                    "uid": get_md5(text),
                    "content": text
                }
            )
            print('R', end='', flush=True)

            count += 1
            if count % 100 == 0:
                print('R', end='', flush=True)
                player_producer.flush()

        player_producer.flush()
        print(' %s\n-------------------------' % count)


def consume_avro_message(consumer, topic, json_obj):
    survey_uid = json_obj['uid']
    content = json_obj['content']


def consume_json_message(consumer, topic, json_obj):
    payload = json.loads(json_obj)['payload']
    response_uid = payload['uid']
    survey_uid = payload['survey_uid']
    data = payload['data']
    return payload


def consume_messages(consumer, n_of_messages):
    count = 0
    temp_count = 0
    messages = dict()
    while True:
        try:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                if count >= n_of_messages:
                    break
                print('No messages')
                temp_count += 1
                if temp_count > 10:
                    break
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Proper message
                topic, value_str = msg.topic(), msg.value()
                # print('%% %s [%d] at offset %d with value %s:\n' % (
                #     topic, msg.partition(), msg.offset(), str(value_str)
                # ))

                json_obj = value_str
                if topic == 'survey_evalese':
                    consume_avro_message(consumer, topic, json_obj)
                elif topic == 'survey_template' :
                    consume_avro_message(consumer, topic, json_obj)
                else:
                    payload = consume_json_message(consumer, topic, json_obj)
                    if topic not in messages:
                        messages[topic] = []
                    messages[topic].append(payload)

                print(
                    'E' if topic == 'survey_evalese' else
                    'T' if topic == 'survey_template' else
                    'S' if topic == 'nlp_process' else
                    'M',
                    end='', flush=True
                )
                count += 1

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
            break

    return messages


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 draupnir.py <yggdrasil_host>")
        exit(1)

    broker_url = '%s:9092' % sys.argv[1]
    schema_registry_url = 'http://%s:8081' % sys.argv[1]

    designer_producer = AvroProducer(
        {
            'bootstrap.servers': broker_url,
            'schema.registry.url': schema_registry_url
        },
        default_value_schema=SURVEY_VALUE_SCHEMA
    )

    player_producer = AvroProducer(
        {
            'bootstrap.servers': broker_url,
            'schema.registry.url': schema_registry_url
        },
        default_value_schema=RESPONSE_VALUE_SCHEMA
    )

    produce_messages(designer_producer, player_producer)

    # player_consumer = AvroConsumer({
    #     'bootstrap.servers': broker_url,
    #     'group.id': 'player_group',
    #     'session.timeout.ms': 6000,
    #     'auto.offset.reset': 'earliest',
    #     'schema.registry.url': schema_registry_url,
    # })
    # player_consumer.subscribe(['survey_evalese', 'survey_json'])
    # consume_messages(player_consumer, 2)
    # player_consumer.close()
    #
    # asgard_consumer = Consumer({
    #     'bootstrap.servers': broker_url,
    #     'group.id': 'asgard_group',
    #     'session.timeout.ms': 6000,
    #     'auto.offset.reset': 'earliest'
    # })
    # asgard_consumer.subscribe(['nlp_process'])
    # consume_messages(asgard_consumer, 1000)
    # asgard_consumer.close()
    #
    # visualizer_consumer = Consumer({
    #     'bootstrap.servers': broker_url,
    #     'group.id': 'visualizer_group',
    #     'session.timeout.ms': 6000,
    #     'auto.offset.reset': 'earliest'
    # })
    # visualizer_consumer.subscribe(['survey_metrics'])
    # messages = consume_messages(visualizer_consumer, 1000)
    # visualizer_consumer.close()
    #
    # write_rows(messages)
