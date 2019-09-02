from neo4j_adapter import Neo4jAdapter


def work_unit(tx, cypher=None):
    return tx.run(cypher)


def find_node_and_relations(context, node_uid, node_label, related_node_label):
    neo4j_adapter = Neo4jAdapter(context.neo4j_conf)
    cypher = """
        MATCH (n:%s {uid: "%s"})-[]-(m:%s)
        RETURN COLLECT(m.uid) AS c
    """ % (node_label, node_uid, related_node_label)
    result = neo4j_adapter.execute_one(work_unit, mode="READ_ACCESS", need_result=True, cypher=cypher)
    return result[0]['c']


def check_if_sentiment_added(context, node_label, node_uid):
    neo4j_adapter = Neo4jAdapter(context.neo4j_conf)
    cypher = """
        MATCH (n:%s {uid: "%s"})
        RETURN EXISTS(n.sentiment) AS e
    """ % (node_label, node_uid)
    result = neo4j_adapter.execute_one(work_unit, mode="READ_ACCESS", need_result=True, cypher=cypher)
    return result[0]['e']
