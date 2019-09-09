from config_handler import ConfigHandler
from neo4j_adapter import Neo4jAdapter

def before_all(context):
    config = ConfigHandler('app.ini')

    app_host = config.get_config_option('bottle', 'host')
    app_port = config.get_config_option('bottle', 'port')
    context.app_uri = 'http://%s:%s/serve' % (app_host, app_port)

    context.neo4j_conf = {
        'server': config.get_config_option('neo4j', 'server'),
        'user': config.get_config_option('neo4j', 'user'),
        'password': config.get_config_option('neo4j', 'password'),
    }
    context.neo4j_adapter = Neo4jAdapter(context.neo4j_conf)

    nlp_host = config.get_config_option('nlp', 'host')
    nlp_port = config.get_config_option('nlp', 'port')
    context.nlp_uri = 'http://%s:%s/?properties={"annotators":"sentiment","outputFormat":"json"}' % (nlp_host, nlp_port)

def after_all(context):
    context.neo4j_adapter.close()
