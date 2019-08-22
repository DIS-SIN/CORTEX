import json
import requests

from confluent_kafka import avro
from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError


SURVEY_VALUE_SCHEMA = """
{
    "value_schema": "{\\"namespace\\": \\"CORTEX\\", \\"name\\": \\"survey\\", \\"type\\": \\"record\\", \\"fields\\": [{\\"name\\": \\"uid\\", \\"type\\": \\"string\\"}, {\\"name\\": \\"format\\", \\"type\\": \\"string\\"}, {\\"name\\": \\"content\\", \\"type\\": \\"string\\"}]}",
    "records": [
        {"value": %s}
    ]
}
"""

RESPONSE_VALUE_SCHEMA = {
    "value_schema": {
        "namespace": "CORTEX",
        "name": "response",
        "type": "record",
        "fields": [
            {"name": "uid", "type": "string"},
            {"name": "content", "type": "string"}
        ]
    }
}

SENTIMENT_VALUE_SCHEMA = {
    "namespace": "CORTEX",
	"name": "sentiment_values",
	"type": "record",
	"fields": [
		{"name": "uid", "type": "string"},
		{
            "name": "data",
            "type": "array",
            "items": [
                {"name": "uid", "type": "string"},
                {"name": "text", "type": "string"}
            ]
        }
	]
}


def before_all(context):
    context.topics = {
        "survey_evalese": "survey_evalese",
        "survey_json": "survey_json",
        "survey_response": "survey_response",
        "nlp_process": "nlp_process",
        "nlp_result": "nlp_result",
        "survey_metrics": "survey_metrics"
    }

    context.rest_proxy_url = context.config.userdata.get("yggdrasil_rest_proxy")
    context.rest_proxy_topic_url = "http://%s/topics" % context.rest_proxy_url
    context.rest_proxy_consumer_url = "http://%s/consumers" % context.rest_proxy_url
    context.rest_proxy_schema = SURVEY_VALUE_SCHEMA

    context.designer_proxy_session = requests.Session()
    context.player_proxy_session = requests.Session()

    context.broker_url = context.config.userdata.get("yggdrasil_broker")
    context.schema_registry_url = "http://%s/" % context.config.userdata.get("yggdrasil_schema_registry")

    context.neo4j_conf = {
        'neo4j_bolt_server': 'bolt://%s' % context.config.userdata.get("jotunheimr"),
        'neo4j_user': 'neo4j',
        'neo4j_password': '##dis@da2019##',
    }

    # context.player_producer = AvroProducer(
    #     {
    #         'bootstrap.servers': context.broker_url,
    #         'schema.registry.url': context.schema_registry_url
    #     },
    #     default_value_schema=avro.loads(RESPONSE_VALUE_SCHEMA)
    # )
    #
    # context.asgard_consumer = AvroConsumer({
    #     'bootstrap.servers': context.broker_url,
    #     'group.id': 'asgard_consumer',
    #     'schema.registry.url': context.schema_registry_url
    # })
    # context.asgard_consumer.subscribe([context.topics["nlp_process"]])
    # context.asgard_producer = AvroProducer(
    #     {
    #         'bootstrap.servers': context.broker_url,
    #         'schema.registry.url': context.schema_registry_url
    #     },
    #     default_value_schema=avro.loads(SENTIMENT_VALUE_SCHEMA)
    # )
    #
    # context.visualiser_consumer.subscribe([context.topics["survey_metrics", "nlp_result"]])


def after_all(context):
    context.designer_proxy_session.close()
    context.player_proxy_session.close()
    # context.asgard_consumer.close()
    # context.visualiser_consumer.close()
    # context.visualiser_neo4j_adapter.close()
