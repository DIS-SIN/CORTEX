# -*- coding: utf-8 -*-
import traceback

from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib

URL_PREFIX = 'https://www.canada.ca'
EN_URI = '/en/government/dept.html'
FR_URI = '/fr/gouvernement/min.html'

headers = ['name', 'url', '']


def scrappe(prefix, uri, lang='en'):
    dept_list = []

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
            dept_list.append(dept)

    except Exception:
        traceback.print_exc()

    return dept_list


def write_rows(rows, file_name):
    with open(file_name, mode='wt', encoding='utf-8') as text_file:
        text_file.write('\t'.join(headers) + '\n')
        for row in rows:
            text_file.write('\t'.join([row[k] for k in headers]) + '\n')
    return len(rows)


if __name__ == '__main__':
    en_dept_list = scrappe(URL_PREFIX, EN_URI)
    print('Scrapped %d [en] departments.' % len(en_dept_list))
    file_name = 'en_goc_dept.tsv'
    count = write_rows(en_dept_list, file_name)

    fr_dept_list = scrappe(URL_PREFIX, FR_URI)
    print('Scrapped %d [fr] departments.' % len(fr_dept_list))
    file_name = 'fr_goc_dept.tsv'
    count = write_rows(fr_dept_list, file_name)
