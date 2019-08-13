# -*- coding: utf-8 -*-
import os.path
from queue import Queue
from threading import Event, Thread
import sys
import time
import traceback

from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib

BASE_URL = 'https://geds-sage.gc.ca'
LIST_PAGE = '?pgid=012'
LANG_PATH = {'en': '/en/GEDS/', 'fr': '/fr/SAGE/'}
HOME_PAGE = {True: '?pgid=027&dn=', False: '?pgid=017&dn='}
TREE_PAGE = '?pgid=014&dn='
headers = [
    'org_dn',
    'org_en_name', 'org_fr_name',
    'org_lc_addr',
    'org_lc_city', 'org_lc_pr', 'org_lc_pc', 'org_lc_ctry'
]
ENT_FILE_NAME = 'geds_orgs.tsv'
REL_FILE_NAME = 'geds_rels.tsv'


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_content_body(pid, session, url):
    # print('[%s] %s ...' % (pid, urllib.parse.unquote(url)))
    text = session.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    return soup.find('body')


def new_entity(org_dn, org_en_name):
    entity = { k: '' for k in headers }
    entity['org_dn'], entity['org_en_name'] = org_dn, org_en_name
    return entity


def get_en_props(pid, session, url, entity, org_en_name):
    body = get_content_body(pid, session, url)
    div_well = body.find('div', {'class': 'well'})
    all_divs = div_well.find_all('div')

    row_count = 0
    for div_tag in div_well.find_all('div'):
        tag_text = div_tag.text.strip()
        if row_count == 0 and tag_text != org_en_name:
            continue

        if row_count == 0:
            pass
        elif row_count == 1:
            entity['org_lc_addr'] = tag_text
        elif row_count == 2:
            entity['org_lc_city'] = tag_text[:tag_text.find(',')].strip()
            entity['org_lc_pr'] = tag_text[tag_text.find(',')+1:-7].strip()
            entity['org_lc_pc'] = tag_text[-7:].replace(' ', '')
        else:
            entity['org_lc_ctry'] = tag_text
            break
        row_count += 1

    return entity


def get_fr_props(pid, session, url, entity):
    body = get_content_body(pid, session, url)
    h3_panel = body.find('h3', {'class': 'panel-title'})
    entity['org_fr_name'] = h3_panel.text.strip()
    return entity


def get_child_orgs(pid, session, url, entity, in_queue, out_queue, org_dn, org_en_name):
    body = get_content_body(pid, session, url)
    org_tree = body.find('div', {'id': 'orgTree'})
    all_links = org_tree.find_all('div', {'class': 'browseLink'})

    found_org = False
    child_count = 0
    for link in all_links:
        a_href = link.find_all('a')[0]
        if not found_org:
            if '?pgid=017' in a_href['href'] or '?pgid=027' in a_href['href']:
                found_org = True
            continue

        chd_org_dn = a_href['href'][13:]
        chd_org_en_name = a_href['title'].strip()
        # print('[in] %s %s' % (chd_org_en_name, urllib.parse.unquote(chd_org_dn)))
        in_queue.put([chd_org_dn, chd_org_en_name])

        # print('[out (R)] %s %s' % (urllib.parse.unquote(org_dn), urllib.parse.unquote(chd_org_dn)))
        print('-', end='', flush=True)
        out_queue.put({'parent': org_dn, 'child': chd_org_dn})
        child_count += 1


def get_org(pid, session, in_queue, out_queue, org_dn, org_en_name):
    entity = new_entity(org_dn, org_en_name)

    is_dept = urllib.parse.unquote(org_dn).lower().count('ou=') == 1
    home_page = HOME_PAGE[is_dept]

    url = BASE_URL + LANG_PATH['en'] + home_page + org_dn
    entity = get_en_props(pid, session, url, entity, org_en_name)
    url = BASE_URL + LANG_PATH['fr'] + home_page + org_dn
    entity = get_fr_props(pid, session, url, entity)

    # print('[out (E)] %s %s' % (urllib.parse.unquote(org_dn), entity))
    print('.', end='', flush=True)
    out_queue.put({'org_dn': org_dn, 'entity': entity})

    url = BASE_URL + LANG_PATH['en'] + TREE_PAGE + org_dn
    get_child_orgs(pid, session, url, entity, in_queue, out_queue, org_dn, org_en_name)


def scrapper(pid, in_queue, out_queue, start_event, stop_event):
    try:
        # print('Start SCRAPPER %s' % pid)
        session = requests_retry_session(session=requests.Session())
        while not stop_event.is_set():
            if in_queue.empty():
                time.sleep(0.1)
                continue

            org_dn, org_en_name = in_queue.get()
            get_org(pid, session, in_queue, out_queue, org_dn, org_en_name)

            if not start_event.is_set():
                start_event.set()

    except Exception as e:
        print('EXCEPTION [process %s] %s ' % (pid, e))
        traceback.print_exc()


def collector(in_queue, out_queue, write_queue, start_event, stop_event):
    entity_rows = []
    relation_rows = []
    key_set = set()
    key_dict = dict()
    counter = 0

    while not start_event.is_set():
        time.sleep(1)

    while not stop_event.is_set():
        if out_queue.empty():
            if in_queue.empty():
                counter += 1
                if counter == 5:
                    stop_event.set()
            else:
                counter = 0
            time.sleep(1)
            continue

        counter = 0
        item = out_queue.get()

        if 'org_dn' in item:
            org_dn = item['org_dn']
            if org_dn is not None:
                if org_dn in key_set:
                    continue
                key_set.add(org_dn)
            entity_rows.append('\t'.join([item['entity'][k] for k in headers]) + '\n')
            # print('%s+ orgs, %s= rels.' % (ent_count, rel_count))

        else:
            if item['parent'] not in key_dict:
                key_dict[item['parent']] = set()
            if item['child'] not in key_dict[item['parent']]:
                key_dict[item['parent']].add(item['child'])
                relation_rows.append('\t'.join([item['parent'], item['child']]) + '\n')
                # print('%s= orgs, %s+ rels.' % (ent_count, rel_count))

    print('\nGot %s organizations.' % len(entity_rows))
    print('Got %s inter-org relations.' % len(relation_rows))
    write_queue.put([entity_rows, relation_rows])


def writer(entity_rows, relation_rows):
    with open(ENT_FILE_NAME, mode='wt', encoding='utf-8') as ent_file:
        ent_file.write('\t'.join(headers) + '\n')
        for row in entity_rows:
            ent_file.write(row)

    with open(REL_FILE_NAME, mode='wt', encoding='utf-8') as rel_file:
        rel_file.write('\t'.join(['parent_org_dn', 'child_org_dn']) + '\n')
        for row in relation_rows:
            rel_file.write(row)

    print('Wrote to file.')


def get_dept_list():
    url = BASE_URL + LANG_PATH['en'] + LIST_PAGE
    body = get_content_body(0, requests_retry_session(), url)
    rows = body.find_all('li', {'class': 'list-group-itemm'})

    dept_list = []
    for row in rows:
        a_href = row.find_all('a')[0]
        org_dn = a_href['href'][13:]
        org_en_name = a_href['title']
        # print('["%s", "%s"]' % (org_dn, org_en_name))
        # print('[%s] in [%s] [%s])' % (pid, org_en_name, org_dn))
        dept_list.append([org_dn, org_en_name])

    print('GOT %s [dept].' % len(dept_list))
    return dept_list


if __name__ == '__main__':
    n_process = 10
    if len(sys.argv) > 1:
        n_process = int(sys.argv[1])

    start_org_dn = None
    start_org_en_name = None
    if len(sys.argv) >= 4:
        start_org_dn = sys.argv[2]
        start_org_en_name = sys.argv[3]

    dept_list = get_dept_list()
    stop_processing = False
    for start_org_dn, start_org_en_name in dept_list:

        is_done, entity_rows, relation_rows = False, None, None
        while not is_done:
            stop_event = Event()
            start_event = Event()
            input_queue = Queue()
            output_queue = Queue()
            write_queue = Queue()

            scrapper_workers = []
            for i in range (0, n_process):
                worker = Thread(
                    target=scrapper,
                    args=(i, input_queue, output_queue, start_event, stop_event, )
                )
                scrapper_workers.append(worker)

            collect_worker = Thread(
                target=collector,
                args=(input_queue, output_queue, write_queue, start_event, stop_event, )
            )

            for worker in scrapper_workers:
                worker.start()
            collect_worker.start()

            input_queue.put([start_org_dn, start_org_en_name])
            print('[PROCESS] %s ' % start_org_en_name)

            try:
                collect_worker.join()
                for worker in scrapper_workers:
                    worker.join()
            except KeyboardInterrupt:
                stop_event.set()
                stop_processing = True
                break

            entity_rows, relation_rows = write_queue.get()
            is_done = len(entity_rows)==len(relation_rows)+1

        if stop_processing:
            break

        writer(entity_rows, relation_rows)
        print('[DONE] %s.\n' % start_org_en_name)
