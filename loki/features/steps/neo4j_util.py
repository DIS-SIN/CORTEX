from neo4j_adapter import Neo4jAdapter


def work_unit(tx, cypher=None):
    return tx.run(cypher)


def find_node_and_count_relations(context, node_uid, node_label, related_node_label):
    neo4j_adapter = Neo4jAdapter(context.neo4j_conf)
    result_uids = []
    cypher = """
        MATCH (n:%s {uid: "%s"})-[r]->(m:%s)
        RETURN COUNT(DISTINCT(r)) AS c, COLLECT(m.uid) AS mc
    """ % (node_label, node_uid, related_node_label)
    result = neo4j_adapter.execute_one(work_unit, mode="READ_ACCESS", need_result=True, cypher=cypher)
    return result[0]['c'], result[0]['mc']
