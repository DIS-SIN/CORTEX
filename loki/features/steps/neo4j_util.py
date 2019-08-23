from neo4j_adapter import Neo4jAdapter


def work_unit(tx, cypher=None):
    return tx.run(cypher)


def find_questions_of_survey(context, survey_uid):
    neo4j_adapter = Neo4jAdapter(context.neo4j_conf)
    result_uids = []
    cypher = """
        MATCH (s:Valhalla_Survey {uid: "%s"})-[:AT_ORDER]->(q:Valhalla_Question)
        RETURN COLLECT(DISTINCT(q.uid)) AS q_uids
    """ % survey_uid
    result = neo4j_adapter.execute_one(work_unit, mode="READ_ACCESS", need_result=True, cypher=cypher)
    return result[0]['q_uids']


def find_number_of_answers(context, response_uid):
    neo4j_adapter = Neo4jAdapter(context.neo4j_conf)
    result_num = []
    cypher = """
        MATCH (s:Valhalla_Response {uid: "%s"})-[r:AT_ORDER]->()
        RETURN COUNT(DISTINCT(r)) AS n
    """ % response_uid
    result = neo4j_adapter.execute_one(work_unit, mode="READ_ACCESS", need_result=True, cypher=cypher)
    return result[0]['n']


def find_metrics_updates(context, question_uid):
    neo4j_adapter = Neo4jAdapter(context.neo4j_conf)
    result_num = []
    cypher = """
        MATCH (s:Valhalla_Question {uid: "%s"})
        RETURN EXISTS(s.stats) AS has_stats
    """ % question_uid
    result = neo4j_adapter.execute_one(work_unit, mode="READ_ACCESS", need_result=True, cypher=cypher)
    return result[0]['has_stats']


def find_free_text_nodes(context, response_uid):
    neo4j_adapter = Neo4jAdapter(context.neo4j_conf)
    result_num = []
    cypher = """
        MATCH (s:FreeText {uid: "%s"})
        RETURN COUNT(s) AS c
    """ % response_uid
    result = neo4j_adapter.execute_one(work_unit, mode="READ_ACCESS", need_result=True, cypher=cypher)
    return result[0]['c']
