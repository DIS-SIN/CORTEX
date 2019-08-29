from confluent_kafka import avro


SURVEY_VALUE_SCHEMA = """
{
    "value_schema": "{\\"namespace\\": \\"CORTEX\\", \\"name\\": \\"Survey\\", \\"type\\": \\"record\\", \\"fields\\": [{\\"name\\": \\"uid\\", \\"type\\": \\"string\\"}, {\\"name\\": \\"format\\", \\"type\\": \\"string\\"}, {\\"name\\": \\"content\\", \\"type\\": \\"string\\"}]}",
    "records": [
        {"value": %s}
    ]
}
"""

RESPONSE_VALUE_SCHEMA = """
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


def before_all(context):

    context.survey_schema = SURVEY_VALUE_SCHEMA
    context.response_schema = avro.loads(RESPONSE_VALUE_SCHEMA)

    context.broker = context.config.userdata.get("yggdrasil_broker")
    context.schema_registry = context.config.userdata.get("yggdrasil_schema_registry")
    context.rest_proxy = context.config.userdata.get("yggdrasil_rest_proxy")
    context.jotunheimr = context.config.userdata.get("jotunheimr")

    context.schema_registry_url = "http://%s" % context.schema_registry

    context.rest_proxy_topic_url = "http://%s/topics" % context.rest_proxy
    context.rest_proxy_consumer_url = "http://%s/consumers" % context.rest_proxy

    context.neo4j_conf = {
        'neo4j_bolt_server': 'bolt://%s' % context.jotunheimr,
        'neo4j_user': 'neo4j',
        'neo4j_password': '##dis@da2019##',
    }
