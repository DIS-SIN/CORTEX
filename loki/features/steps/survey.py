from behave import *
from hash_util import get_content, get_md5
from proxy_util import produce_message_via_proxy, consume_message_via_proxy
from neo4j_util import find_questions_of_survey, find_number_of_answers, find_metrics_updates, find_free_text_nodes
from client_util import produce_message, consume_messages
from time import sleep


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


@given('Thor creates a "{response}" and sent this response via "{topic}" to Jotunheimr')
def step_impl(context, response, topic):
    file_name = '%s.json' % response
    text = get_content(file_name)
    uid = get_md5(text)
    context.response_uid = uid
    produce_message(context, topic, uid, text)


@when('Jotunheimr extracts "{number}" answers')
def step_impl(context, number):
    sleep(3)
    n_of_answers = find_number_of_answers(context, context.response_uid)
    assert int(n_of_answers) == int(number)


@then('it updates aggreagated metrics of "{question_uid}" to contains the received response')
def step_impl(context, question_uid):
    assert find_metrics_updates(context, question_uid) is not None


@then('Asgard receives a free text answer "{text}" via "{topic}"')
def step_impl(context, text, topic):
    found = consume_messages(context, 'asgard_grp', topic, context.response_uid)
    assert found == True


@then('it sends "{value}" as its sentiment value via "{topic}" to Jotuheimr')
def step_impl(context, value, topic):
    pass


@then('Jotunheimr persists this sentiment "{value}" value for "{question_uid}"')
def step_impl(context, value, question_uid):
    pass


@then('metrics of "{survey_uid}" arrive via "{topic}"')
def step_impl(context, survey_uid, topic):
    found = consume_messages(context, 'visualizer_grp', topic, survey_uid)
    assert found == True

@then('the sentiment value {value} also come via "{topic}"')
def step_impl(context, value, topic):
    pass
