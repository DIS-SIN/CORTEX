# -*- coding: utf-8 -*-
import json
import logging
from logging.config import fileConfig
from os import getpid, kill
from queue import Queue
import signal
from threading import Thread, Event, get_ident
from time import sleep

from bottle import HTTPError, run, route, request, response

from config_handler import ConfigHandler
from neo4j_adapter import Neo4jAdapter


fileConfig('logging.ini')
logger = logging.getLogger('appLogger')

config = ConfigHandler('app.ini')
bottle_conf = {
    'host': config.get_config_option('bottle', 'host'),
    'port': int(config.get_config_option('bottle', 'port')),
    'server': config.get_config_option('bottle', 'server'),
    'threads': int(config.get_config_option('bottle', 'threads')),
}

neo4j_conf = {
    'server': config.get_config_option('neo4j', 'server'),
    'user': config.get_config_option('neo4j', 'user'),
    'password': config.get_config_option('neo4j', 'password'),
}

in_queue = Queue()
out_queue_dict = dict()
stop_event = Event()


@route('/shutdown', method=['GET'])
def app_shutdown():
    logger.info('/shutdown invoked.')
    stop_event.set()
    kill(getpid(), signal.SIGINT)


@route('/health-check', method='GET')
def app_info():
    return 'OK'


@route('/reload-config', method='GET')
def app_info():
    config.reload()
    logger.info('/reload-config invoked.')
    return 'Config reloaded.'


@route('/serve/<service>', method='POST')
def serve(service):
    tid = get_ident()

    cypher = config.get_config_option('service', service)
    if not cypher:
        logger.debug('HTTP %s %s' % (400, 'Unknown %s service' % service))
        raise HTTPError(body='Unknown %s service' % service, status=400)
    content = request.json
    logger.info('>>> [%s] /serve/%s %s %s' % (tid, service, cypher, content))

    if tid not in out_queue_dict:
        out_queue_dict[tid] = Queue()
    out_queue = out_queue_dict[tid]

    in_queue.put([tid, cypher, content])
    while out_queue.empty() and not stop_event.is_set():
        sleep(0.1)
    item = out_queue.get()

    if stop_event.is_set():
        logger.debug('HTTP %s %s' % (503, 'Application shutdown.'))
        raise HTTPError(body='Application shutdown.', status=503)

    logger.info('<<< [%s] /serve/%s %s' % (tid, service, item))
    return json.dumps(item)


def work_unit(tx, cypher=None, **kw_args):
    return tx.run(cypher, **kw_args)


def execute(adapter):

    while not stop_event.is_set():
        if in_queue.empty():
            sleep(0.1)
            continue

        tid, cypher, content = in_queue.get()
        r = adapter.execute_one(work_unit, cypher=cypher, **content)
        out_queue_dict[tid].put(r[0]['result'])


if __name__ == '__main__':

    try:
        neo4j_adapter = Neo4jAdapter(neo4j_conf)
        executor = Thread(target=execute, args=(neo4j_adapter,))
        executor.start()
        run(**bottle_conf)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()

    executor.join()
