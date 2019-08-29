import json
import requests


PRODUCER_HDRS = {
    "Content-Type": "application/vnd.kafka.avro.v2+json",
    "Accept": "application/vnd.kafka.v2+json"
}
CONSUMER_HDRS_C = {"Content-Type": "application/vnd.kafka.v2+json"}
CONSUMER_HDRS_A = {"Accept": "application/vnd.kafka.avro.v2+json"}


def produce_message_via_proxy(context, topic, uid, format, content):
    r = requests.post(
        '%s/%s' % (context.rest_proxy_topic_url, topic),
        headers=PRODUCER_HDRS,
        data=context.survey_schema % json.dumps(
            {"uid": uid, "format": format, "content": content}
        )
    )
    return r


def consume_message_via_proxy(context, topic):
    r = requests.post(
        '%s/%s_consumer' % (context.rest_proxy_consumer_url, topic),
        headers=CONSUMER_HDRS_C,
        data='{"name": "%s_instance", "format": "avro", "auto.offset.reset": "earliest"}' % topic
    )
    assert r.status_code == 200 or r.status_code == 409

    r = requests.post(
        '%s/%s_consumer/instances/%s_instance/subscription' % (context.rest_proxy_consumer_url, topic, topic),
        headers=CONSUMER_HDRS_C,
        data='{"topics": ["%s"]}' % topic
    )
    assert r.status_code == 200 or r.status_code == 204

    try:
        r = requests.get(
            '%s/%s_consumer/instances/%s_instance/records' % (context.rest_proxy_consumer_url, topic, topic),
            headers=CONSUMER_HDRS_A,
            timeout=3
        )
    except requests.exceptions.Timeout:
        return ''
    return r.json()
