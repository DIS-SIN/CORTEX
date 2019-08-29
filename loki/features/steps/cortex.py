from behave import *
from hash_util import get_content, get_md5
from proxy_util import produce_message_via_proxy, consume_message_via_proxy
from neo4j_util import find_questions_of_survey, find_number_of_answers, find_metrics_updates, find_free_text_nodes
from client_util import produce_message, consume_messages
from time import sleep


################################################################################
# Scenario: Sending and receiving survey in evalese format
#    Given "designer" creates "test_sur" in "evalese" format
#     When "designer" sends "test_sur" in "evalese" via "survey_evalese" to Yggdrasil
#     Then "player" receives "test_sur" in "evalese" via "survey_evalese" from Yggdrasil

@given('"{sender_name}" creates "{survey_uid}" in "{format}" format')
def step_impl(context, sender, survey_uid, format):
    file_name = '%s_%s.json' % (survey_uid, format)
    file_content = get_content(file_name)
    file_md5 = get_md5(file_content)

    if getattr(context, sender_name) is None:
        setattr(context, sender_name, dict())
    sender = getattr(context, sender_name)
    sender[survey_uid] = dict({
        'md5': file_md5,
        format: file_content
    })


@when('"{sender_name}" sends "{survey_uid}" in "{format}" via "survey_evalese" to Yggdrasil')
def step_impl(context, sender_name, survey_uid, format, topic):
    sender = getattr(context, sender_name)
    content = sender[survey_uid][format]
    r = produce_message_via_proxy(context, topic, survey_uid, format, content)
    assert r.status_code == 200


@then('"{receiver_name}" receives "{survey_uid}" in "{format}" via "survey_evalese" from Yggdrasil')
def step_impl(context, receiver, survey_uid, format, topic):
    if getattr(context, receiver) is None:
        setattr(context, receiver, dict())
    receiver = getattr(context, receiver_name)
    r = consume_message_via_proxy(context, topic)
    assert r.status_code == 200

#
################################################################################
