# -*- coding: utf-8 -*-
import traceback

from bs4 import BeautifulSoup
import requests

GOC_DEPT_URL_PREFIX = 'https://www.canada.ca'
EN_DEPT_LIST_URI = '/en/government/dept.html'
FR_DEPT_LIST_URI = '/fr/gouvernement/min.html'
headers = ['dept_name', 'dept_url', 'dept_abbr']


def scrappe(prefix, uri):

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
                    dept['dept_url'] = a_hrefs[0]['href']
                    if not a_hrefs[0]['href'].startswith('http'):
                        dept['dept_url'] = prefix + a_hrefs[0]['href']
                    dept['dept_name'] = a_hrefs[0].text.strip()
                else:
                    if td.text.strip():
                        dept['dept_abbr'] = td.text.strip()
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
    dept_list = scrappe(GOC_DEPT_URL_PREFIX, EN_DEPT_LIST_URI)
    file_name = 'en_goc_dept.tsv'
    count = write_rows(dept_list, file_name)
    print('Scrapped %d departments into [en_goc_dept.tsv] file.' % count)

    dept_list = scrappe(GOC_DEPT_URL_PREFIX, FR_DEPT_LIST_URI)
    file_name = 'fr_goc_dept.tsv'
    count = write_rows(dept_list, file_name)
    print('Scrapped %d departments into [fr_goc_dept.tsv] file.' % count)
