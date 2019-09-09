import hashlib
import json
from time import sleep

from behave import *

from app_util import send_to_app
from common_util import get_content, get_md5
from neo4j_util import get_apoc_version, find_node_and_relations


################################################################################
#
# Scenario: Check neo4j
#    Given Neo4j is installed with APOC version "3.5.0.4"
#
@given('neo4j is installed with apoc version "{version}"')
def step_impl(context, version):
    assert get_apoc_version(context) == version
#
#
################################################################################

################################################################################
#
# Scenario: Sending and receiving survey in evalese format
#    Given EValhalla Designer creates "TEST_SUR_evalese" in "sur_evalese" format
#     When EValhalla Designer calls "survey" service to "store" it
#     Then EValhalla Player calls "survey" service to "retrieve" it
#
# Scenario: Sending and receiving survey in template format
#    Given EValhalla Designer creates "TEST_SUR_template" in "template" format
#     When EValhalla Designer calls "survey" service to "store" it
#     Then EValhalla Player calls "survey" service to "retrieve" it
#     And Neo4j receives it and creates a "CSPS_Survey" with a number of "CSPS_Question"
#
@given('EValhalla Designer creates "{survey}" in "{format}" format')
def step_impl(context, survey, format):
    file_name = '/data/%s.json' % survey
    content = json.loads(get_content(file_name))
    context.survey_uid = content['uid']
    context.survey_format = format
    if format in content:
        context.survey_content = json.dumps(content[format])
    else:
        context.survey_content = json.dumps(content)


@when('EValhalla Designer calls "{service}" service to "{operation}" it')
def step_impl(context, service, operation):
    md5 = send_to_app(
        context,
        '%s_%s_%s' % (service, operation, context.survey_format),
        json.dumps({'uid': context.survey_uid, 'content': context.survey_content})
    )
    assert md5 == get_md5(context.survey_content)


@then('EValhalla Player calls "{service}" service to "{operation}" it')
def step_impl(context, service, operation):
    content = send_to_app(
        context,
        '%s_%s_%s' % (service, operation, context.survey_format),
        json.dumps({"uid": context.survey_uid})
    )
    assert get_md5(content) == get_md5(context.survey_content)


@then('Neo4j receives it and creates a "{survey_node}" with a number of "{question_node}"')
def step_impl(context, survey_node, question_node):
    question_uid_set = set(
        '%s_q_%s' % (context.survey_uid, q['qid'])
        for q in json.loads(context.survey_content)['questions']
        if q['qid'] != 'none'
    )
    c = find_node_and_relations(context, context.survey_uid, survey_node, question_node)
    assert set(c) == question_uid_set
#
#
################################################################################

################################################################################
#
# Scenario: Sending and receiving a number of survey responses
#    Given EValhalla Player got items from "0" to "1" of "TEST_SUR_responses"
#     When EValhalla Player calls "response" service to "store" each of them
#     Then Neo4j receives them and creates a number of "CSPS_Response" with "CSPS_Respondent" and "CSPS_Answer"
#
@given('EValhalla Player got items from "{lower}" to "{upper}" of "{response}"')
def step_impl(context, lower, upper, response):
    file_name = '/data/%s.json' % response
    file_content = get_content(file_name)
    responses = json.loads(file_content)[int(lower):int(upper)]
    context.responses = []
    for response in responses:
        content = json.dumps(response)
        context.responses.append({
            'content': content,
            'md5': get_md5(content)
        })


@when('EValhalla Player calls "{service}" service to "{operation}" each of them')
def step_impl(context, service, operation):
    results = []
    for response in context.responses:
        result_md5 = send_to_app(
            context,
            '%s_%s' % (service, operation),
            json.dumps({'uid': response['md5'], 'content': response['content']})
        )
        assert result_md5 == response['md5']


@then('Neo4j receives them and creates a number of "{survey_reponse}" with "{survey_respondent}" and "{survey_answer}"')
def step_impl(context, survey_reponse, survey_respondent, survey_answer):
    for response in context.responses:
        c = find_node_and_relations(context, response['md5'], survey_reponse, survey_respondent)
        assert set(c) == {response['md5']}
#
#
################################################################################
