# -*- coding: utf-8 -*-
import traceback

from bs4 import BeautifulSoup
import requests
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
dept_dict = dict()


def new_entity():
    entity = { k: '' for k in headers }
    entity['children'] = dict()
    return entity

def print_entity(entity):
    print([entity[k] for k in headers])
    if entity['children']:
        for name, child in entity['children'].items():
            print_entity(child)


def get_content_body(url):
    print('%s ...' % urllib.parse.unquote(url))
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    return soup.find('body')


def fill_entity(org_dn, org_en_name):
    entity = new_entity()
    entity['org_dn'], entity['org_en_name'] = org_dn, org_en_name
    is_dept = urllib.parse.unquote(org_dn).lower().count('ou=') == 1
    home_page = HOME_PAGE[is_dept]

    body = get_content_body(BASE_URL + LANG_PATH['en'] + home_page + org_dn)
    div_well = body.find('div', {'class': 'well'})
    all_divs = div_well.find_all('div')
    row_count = 0
    for div_tag in div_well.find_all('div'):
        tag_text = div_tag.text.strip()
        if row_count == 0 and tag_text != entity['org_en_name']:
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

    body = get_content_body(BASE_URL + LANG_PATH['fr'] + home_page + org_dn)
    h3_panel = body.find('h3', {'class': 'panel-title'})
    entity['org_fr_name'] = h3_panel.text.strip()

    body = get_content_body(BASE_URL + LANG_PATH['en'] + TREE_PAGE + org_dn)
    org_tree = body.find('div', {'id': 'orgTree'})
    all_links = org_tree.find_all('div', {'class': 'browseLink'})
    row_count = 0
    for link in all_links:
        a_href = link.find_all('a')[0]
        org_en_name = a_href['title'].strip()
        if row_count == 0 and org_en_name != entity['org_en_name']:
            continue
        if org_en_name != entity['org_en_name']:
            child_entity = fill_entity(a_href['href'][13:], org_en_name)
            entity['children'][org_en_name] = child_entity
        row_count += 1

    return entity


def scrappe():
    try:
        text = requests.get(BASE_URL + LANG_PATH['en'] + LIST_PAGE).text
        soup = BeautifulSoup(text, 'html.parser')

        rows = soup.find('body').find_all('li', {'class': 'list-group-itemm'})
        for row in rows:
            a_href = row.find_all('a')[0]
            dept = fill_entity(a_href['href'][13:], a_href['title'])
            print_entity(dept)
            dept_dict[dept['org_dn']] = dept
            exit(0)

    except Exception:
        traceback.print_exc()


def write_rows(rows, file_name, headers):
    with open(file_name, mode='wt', encoding='utf-8') as text_file:
        text_file.write('\t'.join(headers) + '\n')
        for row in rows:
            text_file.write('\t'.join([row[k] for k in headers]) + '\n')
    return len(rows)


if __name__ == '__main__':
    scrappe()
