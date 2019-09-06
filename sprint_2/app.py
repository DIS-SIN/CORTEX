# -*- coding: utf-8 -*-
import logging
from logging.config import fileConfig
from os import getpid, kill
from queue import Queue
import signal
from threading import Thread, Event
from time import sleep

from bottle import run, route

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
neo4j_adapter = Neo4jAdapter(neo4j_conf)

task_queue = Queue()
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


def execute_tasks(queue):

    while not stop_event.is_set():
        if queue.empty():
            sleep(0.1)
        task = queue.get()


if __name__ == '__main__':

    try:
        Thread(target=execute_tasks, args=(task_queue,)).start()
        run(**bottle_conf)
    except KeyboardInterrupt:
        stop_event.set()
        pass
