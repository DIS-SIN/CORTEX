import json
import requests


def produce_message_via_proxy(context, topic, format, content):
    producer_topic_url = '%s/%s' % (context.rest_proxy_topic_url, context.topics[topic])
    topic_url = '%s/%s' % (context.rest_proxy_topic_url, context.topics[topic])
    payload = {"uid": json.loads(content)['uid'], "format": format, "content": content}
    data = context.rest_proxy_schema % json.dumps(payload)
    r = requests.post(topic_url, headers={"Content-Type": "application/vnd.kafka.avro.v2+json", "Accept": "application/vnd.kafka.v2+json"}, data=data)
    return r


def consume_message_via_proxy(context, topic):
    consumer_endpoint_url = '%s/%s' % (context.rest_proxy_consumer_url, '%s_consumer' % context.topics[topic])
    consumer_instance = '%s_instance' % context.topics[topic]
    player_proxy_config = '{"name": "%s", "format": "avro", "auto.offset.reset": "earliest"}' % consumer_instance
    r = requests.post(consumer_endpoint_url, headers={"Content-Type": "application/vnd.kafka.v2+json"}, data=player_proxy_config)
    assert r.status_code == 200 or r.status_code == 409

    consumer_endpoint_subscription_url = '%s/instances/%s/subscription' % (consumer_endpoint_url, consumer_instance)
    player_proxy_topics = '{"topics": ["%s"]}' % context.topics[topic]
    r = requests.post(consumer_endpoint_subscription_url, headers={"Content-Type": "application/vnd.kafka.v2+json"}, data=player_proxy_topics)
    assert r.status_code == 200 or r.status_code == 204

    consumer_endpoint_records_url = '%s/instances/%s/records' % (consumer_endpoint_url, consumer_instance)
    try:
        r = requests.get(consumer_endpoint_records_url, headers={"Accept": "application/vnd.kafka.avro.v2+json"}, timeout=3)
    except requests.exceptions.Timeout:
        return ''
    return r.json()
