# -*- coding: utf-8 -*-
import csv
import traceback

from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib

URL_PREFIX = 'https://www.canada.ca'
EN_URI = '/en/government/dept.html'
FR_URI = '/fr/gouvernement/min.html'

headers = [
    'en_name', 'en_url', 'en_abbr',
    'fr_name', 'fr_url', 'fr_abbr',
]


def scrappe(prefix, uri, lang='en'):
    dept_dict = dict()

    try:
        text = requests.get(prefix + uri).text
        soup = BeautifulSoup(text, 'html.parser')

        rows = soup.find('body').find('tbody').find_all('tr')
        for row in rows:
            td_list = row.find_all('td')
            dept = { k: '' for k in headers }
            for td in td_list:
                a_hrefs = td.find_all('a')
                if a_hrefs:
                    url = a_hrefs[0]['href']
                    if not url.startswith('http'):
                        url = URL_PREFIX + url
                    dept['url'] = url
                    dept['name'] = a_hrefs[0].text.strip()
                else:
                    if td.text.strip():
                        dept['abbr'] = td.text.strip()
            print(dept['name'], dept)
            dept_dict[dept['name']] = dept

    except Exception:
        traceback.print_exc()

    return dept_dict


def load_rows(file_name):
    dept_list = []

    with open(file_name, mode='rt', encoding='utf-8') as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')
        for row in reader:
            dept_list.append({
                k.strip(): row[k].strip() for k in headers if k in row
            })

    return dept_list


def write_rows(rows, file_name):
    with open(file_name, mode='wt', encoding='utf-8') as text_file:
        text_file.write('\t'.join(headers) + '\n')
        for row in rows:
            text_file.write('\t'.join([row[k] for k in headers]) + '\n')
    return len(rows)


if __name__ == '__main__':
    dept_list = load_rows('goc_dept_bilingual.tsv')
    print('Loaded %d departments.' % len(dept_list))

    for uri, lang in [ [EN_URI, 'en'], [FR_URI, 'fr']]:
        dept_dict = scrappe(URL_PREFIX, uri)
        print('Scrapped %d departments from %s.' % (len(dept_dict), uri))
        for dept in dept_list:
            dept['%s_url' % lang] = dept_dict[dept['%s_name' % lang]]['url']

    file_name = 'goc_depts.tsv'
    count = write_rows(dept_list, file_name)
