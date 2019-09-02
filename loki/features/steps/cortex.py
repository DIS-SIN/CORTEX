import json
import random
from time import sleep

from behave import *

from hash_util import get_content, get_md5
from neo4j_util import find_node_and_relations, check_if_sentiment_added
from client_util import produce_player_messages, produce_asgard_message, consume_json_message
from proxy_util import produce_message_via_proxy, consume_message_via_proxy



################################################################################
#
# Scenario: Sending and receiving survey in evalese format
#    Given valhalla designer creates "TEST_SUR" in "evalese" format
#     When valhalla designer sends it via "survey_evalese" to Yggdrasil
#     Then valhalla player receives it from Yggdrasil
#
@given('valhalla designer creates "{survey_uid}" in "{format}" format')
def step_impl(context, survey_uid, format):
    file_name = 'data/%s_%s.json' % (survey_uid, format)
    file_content = get_content(file_name)
    context.survey = {
        'uid': survey_uid,
        'format': format,
        'content': file_content
    }


@when('valhalla designer sends it via "{topic}" to Yggdrasil')
def step_impl(context, topic):
    r = produce_message_via_proxy(context, topic, context.survey)
    context.survey['topic'] = topic
    assert r.status_code == 200
    sleep(3)


@then('valhalla player receives it from Yggdrasil')
def step_impl(context):
    r = consume_message_via_proxy(context, context.survey['topic'])
    survey = r.json()[0]['value']
    assert context.survey['uid'] == survey['uid']
    assert context.survey['format'] == survey['format']
    assert context.survey['content'] == survey['content']
#
#
################################################################################

################################################################################
#
# Scenario: Sending and receiving survey in template format
#    Given valhalla designer creates "TEST_SUR" in "template" format
#     When valhalla designer sends it via "survey_template" to Yggdrasil
#     Then jotunheimr receives it and creates a "Valhalla_Survey" with a number of "Valhalla_Question"
#
@then('jotunheimr receives it and creates a "{survey_node}" with a number of "{question_node}"')
def step_impl(context, survey_node, question_node):
    survey_uid = context.survey['uid']
    question_uid_set = set(
        '%s_q_%s' % (survey_uid, q['qid'])
        for q in json.loads(context.survey['content'])['questions']
        if q['qid'] != 'none'
    )
    c = find_node_and_relations(context, survey_uid, survey_node, question_node)
    assert set(c) == question_uid_set
#
#
################################################################################

################################################################################
#
# Scenario: Sending and receiving a number of survey responses
#    Given valhalla player creates "10" "TEST_SUR" "responses" in "survey_response" format
#     When valhalla player sends them via "survey_response" to Yggdrasil
#     Then jotunheimr receives them and creates a number of "Valhalla_Response" with "Valhalla_Respondent" and "Valhalla_Answer"
#
@given('valhalla player creates from "{skip}" to "{limit}" "{survey_uid}" "{file_format}" in "{format}" format')
def step_impl(context, skip, limit, survey_uid, file_format, format):
    file_name = 'data/%s_%s.json' % (survey_uid, file_format)
    file_content = get_content(file_name)
    context.survey = {
        'uid': survey_uid,
        'format': format,
        'responses': json.loads(file_content)[int(skip):int(skip)+int(limit)]
    }


@when('valhalla player sends them via "{topic}" to Yggdrasil')
def step_impl(context, topic):
    produce_player_messages(context, topic, context.survey['responses'])
    sleep(3)


@then('jotunheimr receives them and creates a number of "{survey_reponse}" with "{survey_respondent}" and "{survey_answer}"')
def step_impl(context, survey_reponse, survey_respondent, survey_answer):
    for response in context.survey['responses']:
        md5 = get_md5(json.dumps(response))
        c = find_node_and_relations(context, md5, survey_reponse, survey_respondent)
        assert set(c) == {md5}
#
#
################################################################################

################################################################################
#
# Scenario: Receiving free text answers and producing sentiment values
#   Given "asgard" receives free text answers via "nlp_process" from Yggdrasil
#    When asgard produces sentiment values via "nlp_result" to Yggdrasil
#    Then jotunheimr updates "Valhalla_Response" with those values
#     And valhalla visualizer receives sentiment values via "nlp_result" and survey metrics via "survey_metrics"
#
@given('"{consumer}" receives free text answers via "{topic}" from Yggdrasil')
def step_impl(context, consumer, topic):
    context.asgard_message = consume_json_message(context, consumer, [topic])


@when('asgard produces sentiment values via "{topic}" to Yggdrasil')
def step_impl(context, topic):
    asgard_message = {
        'uid': context.asgard_message['uid'],
        'survey_uid': context.asgard_message['survey_uid'],
        'data': json.dumps([
            {
                'uid': q['uid'],
                'sentiment': '%s' % random.uniform(-1.0, 1.0),
                'text': q['text']
            } for q in context.asgard_message['data']
        ])
    }
    produce_asgard_message(context, topic, asgard_message)


@then('jotunheimr updates "{survey_response}" with those values')
def step_impl(context, survey_response):
    response_uid = context.asgard_message['uid']
    assert check_if_sentiment_added(context, survey_response, response_uid)


@then('"{consumer}" receives survey metrics via "{topic}"')
def step_impl(context, consumer, topic):
    consume_json_message(context, consumer, [topic])
#
#
################################################################################
