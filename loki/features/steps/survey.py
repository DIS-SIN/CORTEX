from behave import *
from hash_util import get_content, get_md5
from proxy_util import produce_message_via_proxy, consume_message_via_proxy


@given('the Trash collecting system with name "{name}" and id "{uid}" is created in Valhalla Designer')
def step_impl(context, name, uid):
    assert name is not None
    context.survey_name = name
    context.survey_uid = uid


@when('its "{format}" is sent to "{topic}" of Yggdrasil')
def step_impl(context, format, topic):
    file_name = '%s.%s' % (context.survey_name, format)
    text = get_content(file_name)
    r = produce_message_via_proxy(context, topic, context.survey_uid, format, text)
    assert r.status_code == 200


@then('Valhalla Player should receive via "{topic}" an evalese with md5 "{md5}"')
def step_impl(context, topic, md5):
    response = consume_message_via_proxy(context, topic)
    assert get_md5(response[0]['value']['content']) == md5


@then('Jotunheimr should receive via "{topic}" a json with md5 "{md5}"')
def step_impl(context, topic, md5):
    response = consume_message_via_proxy(context, topic)
    assert get_md5(response[0]['value']['content']) == md5
