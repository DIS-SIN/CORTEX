# -*- coding: utf-8 -*-
from multiprocessing import Event, Process, Manager
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

manager = Manager()
stop_event = Event()

dept_dict = dict()


def new_entity(org_dn, org_en_name):
    entity = { k: '' for k in headers }
    entity['org_dn'], entity['org_en_name'] = org_dn, org_en_name
    return entity


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
    print('[%s] %s ...' % (pid, urllib.parse.unquote(url)))
    text = session.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    return soup.find('body')


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
            entity['org_lc_addr'] = tag_text
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
        chd_org_dn = a_href['href'][13:]
        chd_org_en_name = a_href['title'].strip()
        if not found_org:
            if chd_org_en_name == org_en_name:
                found_org = True
            continue
        if chd_org_en_name != org_en_name:
            print('[in] %s %s' % (chd_org_en_name, urllib.parse.unquote(chd_org_dn)))
            in_queue.put([chd_org_dn, chd_org_en_name])
            print('[out (R)] %s %s' % (urllib.parse.unquote(org_dn), urllib.parse.unquote(chd_org_dn)))
            out_queue.put({'parent': org_dn, 'child': chd_org_dn})
            child_count += 1
    print('ADDED [child] %s' % child_count)


def get_org(pid, session, in_queue, out_queue, org_dn, org_en_name):
    entity = new_entity(org_dn, org_en_name)
    is_dept = urllib.parse.unquote(org_dn).lower().count('ou=') == 1
    home_page = HOME_PAGE[is_dept]

    url = BASE_URL + LANG_PATH['en'] + home_page + org_dn
    entity = get_en_props(pid, session, url, entity, org_en_name)

    url = BASE_URL + LANG_PATH['fr'] + home_page + org_dn
    entity = get_fr_props(pid, session, url, entity)

    print('[out (E)] %s %s' % (urllib.parse.unquote(org_dn), entity))
    out_queue.put({'org_dn': org_dn, 'entity': entity})

    url = BASE_URL + LANG_PATH['en'] + TREE_PAGE + org_dn
    get_child_orgs(pid, session, url, entity, in_queue, out_queue, org_dn, org_en_name)


def get_dept_list(pid, session, in_queue):
    url = BASE_URL + LANG_PATH['en'] + LIST_PAGE
    body = get_content_body(pid, session, url)
    rows = body.find_all('li', {'class': 'list-group-itemm'})
    for row in rows:
        a_href = row.find_all('a')[0]
        org_dn = a_href['href'][13:]
        org_en_name = a_href['title']
        print('[in] %s %s' % (org_en_name, urllib.parse.unquote(org_dn)))
        in_queue.put([org_dn, org_en_name])
    print('ADDED [dept] %s' % len(rows))


def scrapper(pid, in_queue, out_queue):
    try:
        print('Start process %s' % pid)
        session = requests_retry_session(session=requests.Session())

        counter = 0
        while not stop_event.is_set():
            if in_queue.empty():
                time.sleep(1)
                counter += 1
                if counter == 3:
                    break
                continue
            counter = 0

            org_dn, org_en_name = in_queue.get()
            if org_dn is None:
                get_dept_list(pid, session, in_queue)
            else:
                get_org(pid, session, in_queue, out_queue, org_dn, org_en_name)

    except Exception as e:
        print('EXCEPTION [process %s] %s ' % (pid, e))
        traceback.print_exc()


def write_entities(value_dict, file_name, headers):
    with open(file_name, mode='wt', encoding='utf-8') as text_file:
        text_file.write('\t'.join(headers) + '\n')
        for k in sorted(value_dict.keys()):
            row = value_dict[k]
            text_file.write('\t'.join([row[k] for k in headers]) + '\n')


def write_relations(value_dict, file_name):
    with open(file_name, mode='wt', encoding='utf-8') as text_file:
        text_file.write('\t'.join(['parent_org_dn', 'child_org_dn']) + '\n')
        for k in sorted(value_dict.keys()):
            children = value_dict[k]
            for child in children:
                text_file.write('\t'.join([k, child]) + '\n')


if __name__ == '__main__':
    n_process = 10
    if len(sys.argv) > 1:
        n_process = int(sys.argv[1])

    start_org_dn = None
    start_org_en_name = None
    if len(sys.argv) > 3:
        start_org_dn = sys.argv[2]
        start_org_en_name = sys.argv[3]

    input_queue = manager.Queue()
    output_queue = manager.Queue()
    input_queue.put([start_org_dn, start_org_en_name])
    # input_queue.put(['OU%3Datssc-scdata%2CO%3Dgc%2CC%3Dca', 'Administrative Tribunals Support Service of Canada'])

    workers = []
    for i in range (0, n_process):
        worker = Process(target=scrapper, args=(i, input_queue, output_queue))
        workers.append(worker)

    for worker in workers:
        worker.start()

    try:
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        stop_event.set()

    entity_dict = dict()
    relation_dict = dict()
    while not output_queue.empty():
        item = output_queue.get()
        if 'org_dn' in item:
            entity_dict[item['org_dn']] = item['entity']
        else:
            if item['parent'] not in relation_dict:
                relation_dict[item['parent']] = set()
            relation_dict[item['parent']].add(item['child'])

    write_entities(entity_dict, 'geds_orgs.tsv', headers)
    write_relations(relation_dict, 'geds_rels.tsv')

    print('Got %s organizations.' % len(entity_dict))
    print('Got %s inter-org relations.' % sum([len(v) for v in relation_dict.values()]))
