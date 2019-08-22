from behave import *
from hash_util import get_content, get_md5
from proxy_util import produce_message_via_proxy, consume_message_via_proxy
from neo4j_util import find_questions_of_survey


@given('the Trash collecting system with name "{name}" is created in Valhalla Designer')
def step_impl(context, name):
    assert name is not None
    context.survey_name = name


@when('its "{format}" is sent to "{topic}" of Yggdrasil')
def step_impl(context, format, topic):
    file_name = '%s_%s.json' % (context.survey_name, format)
    text = get_content(file_name)
    r = produce_message_via_proxy(context, topic, format, text)
    assert r.status_code == 200


@then('Valhalla Player should receive via "{topic}" an evalese with md5 "{md5}"')
def step_impl(context, topic, md5):
    response = consume_message_via_proxy(context, topic)
    assert get_md5(response[0]['value']['content']) == md5


@then('a json with md5 "{md5}" is delivered via "{topic}"')
def step_impl(context, topic, md5):
    response = consume_message_via_proxy(context, topic)
    assert get_md5(response[0]['value']['content']) == md5


@then('Jotunheimr should receive "{survey_uid}" survey with "{question_uids}" questions')
def step_impl(context, survey_uid, question_uids):
    q_uids = ['%s_%s' % (survey_uid, q_uid.strip()) for q_uid in question_uids.split(',')]
    r_uids = find_questions_of_survey(context, survey_uid)
    assert sorted(r_uids) == sorted(q_uids)


@given('Thor creates a "{response}" to "{name}" survey')
def step_impl(context, response, name):
    pass


@when('he sent this response via "{topic}" to Jotunheimr')
def step_impl(context, topic):
    pass


@then('Jotunheimr extracts "{number}" answers')
def step_impl(context, number):
    pass


@then('updates aggreagated metricsto contains response "{type}" from "{datetime}"')
def step_impl(context, type, datetime):
    pass


@then('and send free text answers via "{topic}" to Asgard')
def step_impl(context, topic):
    pass


@given('Asgard receives a free text answer "{text}" via "{topic}"')
def step_impl(context, text, topic):
    pass


@when('it sends "{value}" as its sentiment value via "{topic}" to Jotuheimr')
def step_impl(context, name):
    pass


@then('Jotunheimr persists this sentiment "{value}" value for "{question_uid}"')
def step_impl(context, name):
    pass


@given('the Visualizer queries responses for "{survey}"')
def step_impl(context, name):
    pass


@when('metrics arrive via "{topic}"')
def step_impl(context, name):
    pass


@then('sentiment value {value} also come via "{topic}"')
def step_impl(context, value name):
    pass
