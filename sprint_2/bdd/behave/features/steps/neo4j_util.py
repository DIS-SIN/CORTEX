def work_unit(tx, cypher=None):
    return tx.run(cypher)


def get_apoc_version(context):
    cypher = """
        RETURN apoc.version() AS v
    """
    result = context.neo4j_adapter.execute_one(work_unit, mode="READ_ACCESS", need_result=True, cypher=cypher)
    return result[0]['v']


def find_node_and_relations(context, node_uid, node_label, related_node_label):
    cypher = """
        MATCH (n:%s {uid: "%s"})-[]-(m:%s)
        RETURN COLLECT(m.uid) AS c
    """ % (node_label, node_uid, related_node_label)
    result = context.neo4j_adapter.execute_one(work_unit, mode="READ_ACCESS", need_result=True, cypher=cypher)
    return result[0]['c']
