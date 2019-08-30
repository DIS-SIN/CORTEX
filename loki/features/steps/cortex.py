import json
from behave import *
from hash_util import get_content, get_md5
from proxy_util import produce_message_via_proxy, consume_message_via_proxy
from neo4j_util import find_node_and_count_relations
from time import sleep


################################################################################
#
# Scenario: Sending and receiving survey in evalese format
#    Given "designer" creates "test_sur" in "evalese" format
#     When "designer" sends "test_sur" in "evalese" via "survey_evalese" to Yggdrasil
#     Then "player" receives "test_sur" in "evalese" via "survey_evalese" from Yggdrasil

@given('"{sender_name}" creates "{survey_uid}" in "{format}" format')
def step_impl(context, sender_name, survey_uid, format):
    file_name = 'data/%s_%s.json' % (survey_uid, format)
    file_content = get_content(file_name)
    file_md5 = get_md5(file_content)

    if not hasattr(context, sender_name):
        setattr(context, sender_name, dict())
    sender = getattr(context, sender_name)
    sender[survey_uid] = dict({
        'md5': file_md5,
        format: file_content
    })


@when('"{sender_name}" sends "{survey_uid}" in "{format}" format via "{topic}" to Yggdrasil')
def step_impl(context, sender_name, survey_uid, format, topic):
    sender = getattr(context, sender_name)
    content = sender[survey_uid][format]
    r = produce_message_via_proxy(context, topic, survey_uid, format, content)
    assert r.status_code == 200


@then('"{receiver_name}" receives "{survey_uid}" in "{format}" format via "{topic}" from Yggdrasil')
def step_impl(context, receiver_name, survey_uid, format, topic):
    if not hasattr(context, receiver_name):
        setattr(context, receiver_name, dict())
    receiver = getattr(context, receiver_name)
    r = consume_message_via_proxy(context, topic)

#
################################################################################

################################################################################
#
# Scenario: Sending and receiving survey in template format
#    Given "valhalla designer" creates "TEST_SUR" in "template" format
#     When "valhalla designer" sends "TEST_SUR" in "template" format via "survey_template" to Yggdrasil
#     Then "jotunheimr" receives "TEST_SUR" in "template" format from "valhalla designer"
#     And "jotunheimr" creates "Valhalla_Survey" and "15" of "Valhalla_Question"

@then('"{receiver_name}" receives "{survey_uid}" in "{format}" format from "{sender_name}"')
def step_impl(context, receiver_name, survey_uid, format, sender_name):
    sender = getattr(context, sender_name)
    content = sender[survey_uid][format]
    context.survey_uid = survey_uid
    context.question_uids = set(
        '%s_q_%s' % (survey_uid, q['qid'])
        for q in json.loads(content)['questions']
        if q['qid'] != 'none'
    )

@then('it creates a "{node_label}" and "{count}" of "{related_node_label}"')
def step_impl(context, node_label, count, related_node_label):
    c, mc = find_node_and_count_relations(context, context.survey_uid, node_label, related_node_label)
    assert int(c) == len(context.question_uids)
    assert set(mc) == context.question_uids

#
################################################################################
