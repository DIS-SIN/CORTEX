from config_handler import ConfigHandler
from neo4j_adapter import Neo4jAdapter

def before_all(context):
    config = ConfigHandler('app.ini')
    context.neo4j_conf = {
        'server': config.get_config_option('neo4j', 'server'),
        'user': config.get_config_option('neo4j', 'user'),
        'password': config.get_config_option('neo4j', 'password'),
    }
    app_host = config.get_config_option('bottle', 'host')
    app_port = config.get_config_option('bottle', 'port')
    context.app_uri = 'http://%s:%s/serve' % (app_host, app_port)
    context.neo4j_adapter = Neo4jAdapter(context.neo4j_conf)

def after_all(context):
    context.neo4j_adapter.close()
