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
    # print('[%s] %s ...' % (pid, urllib.parse.unquote(url)))
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
        out_queue.put({'parent': org_dn, 'child': chd_org_dn})
        child_count += 1

    # if child_count > 0:
    #     print('[%s] ADDED [child] %s' % (pid, child_count))
    # else:
    #     print('[%s] LEAF %s' % (pid, org_en_name))


def get_org(pid, session, in_queue, out_queue, org_dn, org_en_name):
    entity = new_entity(org_dn, org_en_name)

    is_dept = urllib.parse.unquote(org_dn).lower().count('ou=') == 1
    home_page = HOME_PAGE[is_dept]

    url = BASE_URL + LANG_PATH['en'] + home_page + org_dn
    entity = get_en_props(pid, session, url, entity, org_en_name)
    url = BASE_URL + LANG_PATH['fr'] + home_page + org_dn
    entity = get_fr_props(pid, session, url, entity)

    # print('[out (E)] %s %s' % (urllib.parse.unquote(org_dn), entity))
    out_queue.put({'org_dn': org_dn, 'entity': entity})

    url = BASE_URL + LANG_PATH['en'] + TREE_PAGE + org_dn
    get_child_orgs(pid, session, url, entity, in_queue, out_queue, org_dn, org_en_name)


def scrapper(pid, in_queue, out_queue, stop_event):
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


def writer(in_queue, out_queue, info_queue, start_event, stop_event):
    # print('Start WRITER.')

    if os.path.isfile(ENT_FILE_NAME):
        ent_file = open(ENT_FILE_NAME, mode='at', encoding='utf-8')
    else:
        ent_file = open(ENT_FILE_NAME, mode='wt', encoding='utf-8')
        ent_file.write('\t'.join(headers) + '\n')

    if os.path.isfile(REL_FILE_NAME):
        rel_file = open(REL_FILE_NAME, mode='at', encoding='utf-8')
    else:
        rel_file = open(REL_FILE_NAME, mode='wt', encoding='utf-8')
        rel_file.write('\t'.join(['parent_org_dn', 'child_org_dn']) + '\n')

    ent_count = 0
    rel_count = 0
    while not start_event.is_set():
        time.sleep(1)

    counter = 0
    key_set = set()
    key_dict = dict()
    while not stop_event.is_set():
        if out_queue.empty():
            if not in_queue.empty():
                continue
            time.sleep(1)
            counter += 1
            if counter == 3:
                stop_event.set()
            continue

        counter = 0
        item = out_queue.get()
        # print(item)
        if 'org_dn' in item:
            org_dn = item['org_dn']
            if org_dn is not None:
                if org_dn in key_set:
                    continue
                key_set.add(org_dn)

            row = item['entity']
            ent_file.write('\t'.join([row[k] for k in headers]) + '\n')
            ent_count += 1
            if ent_count % 100 == 0:
                ent_file.flush()
            print('.', end='', flush=True)
            # print('%s+ orgs, %s= rels.' % (ent_count, rel_count))

        else:
            if item['parent'] not in key_dict:
                key_dict[item['parent']] = set()
            if item['child'] not in key_dict[item['parent']]:
                key_dict[item['parent']].add(item['child'])
                rel_file.write('\t'.join([item['parent'], item['child']]) + '\n')
                rel_count += 1
                if rel_count % 100 == 0:
                    rel_file.flush()
                print('-', end='', flush=True)
                # print('%s= orgs, %s+ rels.' % (ent_count, rel_count))

    ent_file.close()
    rel_file.close()

    print('\nGot %s organizations.' % ent_count)
    print('Got %s inter-org relations.' % rel_count)
    info_queue.put([ent_count, rel_count])


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
    for start_org_dn, start_org_en_name in dept_list:
        start_event = Event()
        stop_event = Event()

        input_queue = Queue()
        output_queue = Queue()
        info_queue = Queue()

        scrapper_workers = []
        for i in range (0, n_process):
            worker = Thread(
                target=scrapper,
                args=(i, input_queue, output_queue, stop_event, )
            )
            scrapper_workers.append(worker)

        writer_worker = Thread(
            target=writer,
            args=(input_queue, output_queue, info_queue, start_event, stop_event, )
        )

        for worker in scrapper_workers:
            worker.start()
        writer_worker.start()

        input_queue.put([start_org_dn, start_org_en_name])
        print('[PROCESS] %s ' % start_org_en_name)

        try:
            writer_worker.join()
            for worker in scrapper_workers:
                worker.join()
        except KeyboardInterrupt:
            stop_event.set()

        ent_count, rel_count = info_queue.get()
        assert ent_count == rel_count + 1
        print('[DONE] %s.\n' % start_org_en_name)

    # [
    #     ["ou%3DATSSC-SCDATA%2Co%3DGC%2Cc%3DCA", "Administrative Tribunals Support Service of Canada"],
    #     ["OU%3DAAFC-AAC%2CO%3DGC%2CC%3DCA", "Agriculture and Agri-Food Canada"],
    #     ["ou%3DAPEX-APEX%2C+o%3DGC%2C+c%3DCA", "Association of Professional Executives of the Public Service of Canada"],
    #     ["ou%3DACOA-APECA%2C+o%3DGC%2C+c%3DCA", "Atlantic Canada Opportunities Agency"],
    #     ["ou%3DAPA-APA%2C+o%3DGC%2C+c%3DCA", "Atlantic Pilotage Authority"],
    #     ["ou%3DAECL-EACL%2C+o%3DGC%2C+c%3DCA", "Atomic Energy of Canada Limited"],
    #     ["ou%3DOAG-BVG%2C+o%3DGC%2C+c%3DCA", "Auditor General of Canada, Office of the"],
    #     ["ou%3DBOC-BDC%2C+o%3DGC%2C+c%3DCA", "Bank of Canada"],
    #     ["ou%3DCBSA-ASFC%2C+o%3DGC%2C+c%3DCA", "Canada Border Services Agency"],
    #     ["ou%3DCC-CAC%2C+o%3DGC%2C+c%3DCA", "Canada Council for the Arts"],
    #     ["ou%3DCDIC-SADC%2C+o%3DGC%2C+c%3DCA", "Canada Deposit Insurance Corporation"],
    #     ["OU%3DCED-DEC%2CO%3DGC%2CC%3DCA", "Canada Economic Development for Quebec Regions"],
    #     ["ou%3DCIRB-CCRI%2C+o%3DGC%2C+c%3DCA", "Canada Industrial Relations Board"],
    #     ["ou%3DCMHC-SCHL%2C+o%3DGC%2C+c%3DCA", "Canada Mortgage and Housing Corporation"],
    #     ["ou%3DCRA-ARC%2C+o%3DGC%2C+c%3DCA", "Canada Revenue Agency"],
    #     ["ou%3DCSPS-EFPC%2C+o%3DGC%2C+c%3DCA", "Canada School of Public Service"],
    #     ["ou%3DCATSA-ACSTA%2C+o%3DGC%2C+c%3DCA", "Canadian Air Transport Security Authority"],
    #     ["ou%3DCCOHS-CCHST%2C+o%3DGC%2C+c%3DCA", "Canadian Centre for Occupational Health and Safety"],
    #     ["ou%3DCCSA-CCLT%2C+o%3DGC%2C+c%3DCA", "Canadian Centre on Substance Abuse"],
    #     ["ou%3DCCC-CCC%2C+o%3DGC%2C+c%3DCA", "Canadian Commercial Corporation"],
    #     ["ou%3DCCPERB-CCEEBC%2Co%3DGC%2Cc%3DCA", "Canadian Cultural Property Export Review Board"],
    #     ["ou%3DCDC-CCL%2C+o%3DGC%2C+c%3DCA", "Canadian Dairy Commission"],
    #     ["ou%3DCEAA-ACEE%2C+o%3DGC%2C+c%3DCA", "Canadian Environmental Assessment Agency"],
    #     ["ou%3DCFIA-ACIA%2C+o%3DGC%2C+c%3DCA", "Canadian Food Inspection Agency"],
    #     ["ou%3DCGC-CCG%2C+o%3DGC%2C+c%3DCA", "Canadian Grain Commission"],
    #     ["ou%3DPCH-PCH%2C+o%3DGC%2C+c%3DCA", "Canadian Heritage"],
    #     ["ou%3DCHRC-CCDP%2C+o%3DGC%2C+c%3DCA", "Canadian Human Rights Commission"],
    #     ["ou%3DCHRT-TCDP%2C+o%3DGC%2C+c%3DCA", "Canadian Human Rights Tribunal"],
    #     ["ou%3DCIHR-IRSC%2C+o%3DGC%2C+c%3DCA", "Canadian Institutes of Health Research"],
    #     ["ou%3DCICS-SCIC%2C+o%3DGC%2C+c%3DCA", "Canadian Intergovernmental Conference Secretariat"],
    #     ["ou%3DCITT-TCCE%2C+o%3DGC%2C+c%3DCA", "Canadian International Trade Tribunal"],
    #     ["ou%3DCJC-CCM%2C+o%3DGC%2C+c%3DCA", "Canadian Judicial Council"],
    #     ["ou%3DCMHR-MCDP%2C+o%3DGC%2C+c%3DCA", "Canadian Museum for Human Rights"],
    #     ["ou%3DCMH-MCH%2CO%3DGC%2CC%3DCA", "Canadian Museum of History"],
    #     ["ou%3DCMIP-MCIQ%2Co%3DGC%2Cc%3DCA", "Canadian Museum of Immigration at Pier 21"],
    #     ["ou%3DCMN-MCN%2C+o%3DGC%2C+c%3DCA", "Canadian Museum of Nature"],
    #     ["ou%3DCanNor-CanNor%2C+o%3DGC%2C+c%3DCA", "Canadian Northern Economic Development Agency"],
    #     ["ou%3DCNSC-CCSN%2C+o%3DGC%2C+c%3DCA", "Canadian Nuclear Safety Commission"],
    #     ["ou%3DCRTC-CRTC%2C+o%3DGC%2C+c%3DCA", "Canadian Radio-television and Telecommunications Commission"],
    #     ["ou%3DCSIS-SCRS%2C+o%3DGC%2C+c%3DCA", "Canadian Security Intelligence Service"],
    #     ["ou%3DCSA-ASC%2C+o%3DGC%2C+c%3DCA", "Canadian Space Agency"],
    #     ["ou%3DCTC-CCT%2C+o%3DGC%2C+c%3DCA", "Canadian Tourism Commission"],
    #     ["ou%3DCTA-OTC%2C+o%3DGC%2C+c%3DCA", "Canadian Transportation Agency"],
    #     ["ou%3DCBC-RC%2C+o%3DGC%2C+c%3DCA", "CBC/Radio-Canada"],
    #     ["OU%3DCRCC-CCETP%2CO%3DGC%2CC%3DCA", "Civilian Review and Complaints Commission for the RCMP"],
    #     ["ou%3DCSEC-CSTC%2C+o%3DGC%2C+c%3DCA", "Communications Security Establishment Canada"],
    #     ["ou%3DCT-TC%2C+o%3DGC%2C+c%3DCA", "Competition Tribunal"],
    #     ["ou%3DCB-CDA%2C+o%3DGC%2C+c%3DCA", "Copyright Board Canada"],
    #     ["ou%3DCSC-SCC%2C+o%3DGC%2C+c%3DCA", "Correctional Service Canada"],
    #     ["ou%3DCMAC-CACM%2C+o%3DGC%2C+c%3DCA", "Court Martial Appeal Court of Canada"],
    #     ["ou%3DCAS-SATJ%2C+o%3DGC%2C+c%3DCA", "Courts Administration Service"],
    #     ["ou%3DDCC-CDC%2C+o%3DGC%2C+c%3DCA", "Defence Construction Canada"],
    #     ["ou%3DDRDC-RDDC%2C+o%3DGC%2C+c%3DCA", "Defence Research and Development Canada (DRDC,"],
    #     ["ou%3DDI-ID%2Co%3DGC%2Cc%3DCA", "Democratic Institutions"],
    #     ["ou%3DESDC-EDSC%2C+o%3DGC%2C+c%3DCA", "Employment and Social Development Canada"],
    #     ["ou%3DECCC-ECCC%2C+o%3DGC%2C+c%3DCA", "Environment and Climate Change Canada"],
    #     ["ou%3DFCC-FAC%2C+o%3DGC%2C+c%3DCA", "Farm Credit Canada"],
    #     ["ou%3DFPCC-CPAC%2C+o%3DGC%2C+c%3DCA", "Farm Products Council of Canada"],
    #     ["ou%3DFCT-CF%2C+o%3DGC%2C+c%3DCA", "Federal Court"],
    #     ["ou%3DFCA-CAF%2C+o%3DGC%2C+c%3DCA", "Federal Court of Appeal"],
    #     ["OU%3DFDO-FDO%2CO%3DGC%2CC%3DCA", "Federal Economic Development Agency for Southern Ontario"],
    #     ["OU%3DPSLREB-CRTEFP%2CO%3DGC%2CC%3DCA", "Federal Public Sector Labour Relations and Employment Board"],
    #     ["ou%3DFIN-FIN%2C+o%3DGC%2C+c%3DCA", "Finance Canada"],
    #     ["ou%3DFCAC-ACFC%2C+o%3DGC%2C+c%3DCA", "Financial Consumer Agency of Canada"],
    #     ["ou%3DFINTRAC-CANAFE%2C+o%3DGC%2C+c%3DCA", "Financial Transactions and Reports Analysis Centre of Canada"],
    #     ["ou%3DDFO-MPO%2C+o%3DGC%2C+c%3DCA", "Fisheries and Oceans Canada"],
    #     ["ou%3DGAC-AMC%2CO%3DGC%2CC%3DCA", "Global Affairs Canada"],
    #     ["ou%3DGG-GG%2C+o%3DGC%2C+c%3DCA", "Governor General"],
    #     ["ou%3DHPA-APH%2C+o%3DGC%2C+c%3DCA", "Halifax Port Authority"],
    #     ["ou%3DHC-SC%2C+o%3DGC%2C+c%3DCA", "Health Canada"],
    #     ["ou%3DHoC-CdC%2C+o%3DGC%2C+c%3DCA", "House of Commons"],
    #     ["ou%3DIRB-CISR%2C+o%3DGC%2C+c%3DCA", "Immigration and Refugee Board of Canada"],
    #     ["ou%3DIRCC-IRCC%2C+o%3DGC%2C+c%3DCA", "Immigration, Refugees and Citizenship Canada"],
    #     ["ou%3DIRSAS-SAPI%2Co%3DGC%2Cc%3DCA", "Indian Residential Schools Adjudication Secretariat"],
    #     ["ou%3DINAC-AANC%2C+o%3DGC%2C+c%3DCA", "Indigenous and Northern Affairs Canada"],
    #     ["ou%3DISC-SAC%2Co%3DGC%2Cc%3DCA", "Indigenous Services Canada"],
    #     ["ou%3DINFC-INFC%2C+o%3DGC%2C+c%3DCA", "Infrastructure Canada"],
    #     ["ou%3DCSTMC-SMSTC%2C+o%3DGC%2C+c%3DCA", "Ingenium"],
    #     ["ou%3DISED-ISDE%2C+o%3DGC%2C+c%3DCA", "Innovation, Science and Economic Development Canada"],
    #     ["ou%3DIANAIT-AINCI%2Co%3DGC%2Cc%3DCA", "Intergovernmental and Northern Affairs and Internal Trade"],
    #     ["ou%3DIDRC-CRDI%2C+o%3DGC%2C+c%3DCA", "International Development Research Centre"],
    #     ["ou%3DIJC-CMI%2C+o%3DGC%2C+c%3DCA", "International Joint Commission"],
    #     ["ou%3DJUS-JUS%2C+o%3DGC%2C+c%3DCA", "Justice Canada"],
    #     ["ou%3DLPA-APL%2C+o%3DGC%2C+c%3DCA", "Laurentian Pilotage Authority Canada"],
    #     ["ou%3DLAC-BAC%2C+o%3DGC%2C+c%3DCA", "Library and Archives Canada"],
    #     ["OU%3DLOP-BDP%2CO%3DGC%2CC%3DCA", "Library of Parliament"],
    #     ["ou%3DMGERC-CEEGM%2C+o%3DGC%2C+c%3DCA", "Military Grievances External Review Committee"],
    #     ["ou%3DMPCC-CPPM%2C+o%3DGC%2C+c%3DCA", "Military Police Complaints Commission of Canada"],
    #     ["ou%3DNAC-CNA%2C+o%3DGC%2C+c%3DCA", "National Arts Centre"],
    #     ["ou%3DNCC-CCN%2C+o%3DGC%2C+c%3DCA", "National Capital Commission"],
    #     ["OU%3DDND-MDN%2CO%3DGC%2CC%3DCA", "National Defence"],
    #     ["ou%3DNEB-ONE%2C+o%3DGC%2C+c%3DCA", "National Energy Board"],
    #     ["ou%3DNFB-ONF%2C+o%3DGC%2C+c%3DCA", "National Film Board of Canada"],
    #     ["ou%3DNGC-MBAC%2C+o%3DGC%2C+c%3DCA", "National Gallery of Canada"],
    #     ["ou%3DNRC-CNRC%2C+o%3DGC%2C+c%3DCA", "National Research Council Canada"],
    #     ["ou%3DNRCAN-RNCAN%2C+o%3DGC%2C+c%3DCA", "Natural Resources Canada"],
    #     ["ou%3DNSERC-CRSNG%2C+o%3DGC%2C+c%3DCA", "Natural Sciences and Engineering Research Council of Canada"],
    #     ["ou%3DNPA-APN%2C+o%3DGC%2C+c%3DCA", "Northern Pipeline Agency"],
    #     ["ou%3DCEO-DGE%2Co%3DGC%2Cc%3DCA", "Office of the Chief Electoral Officer"],
    #     ["ou%3DFJA-CMF%2C+o%3DGC%2C+c%3DCA", "Office of the Commissioner for Federal Judicial Affairs Canada"],
    #     ["ou%3DOCL-CAL%2C+o%3DGC%2C+c%3DCA", "Office of the Commissioner of Lobbying of Canada"],
    #     ["ou%3DOCOL-COLO%2C+o%3DGC%2C+c%3DCA", "Office of the Commissioner of Official Languages"],
    #     ["ou%3DOCSEC-BCCST%2C+o%3DGC%2C+c%3DCA", "Office of the Communications Security Establishment Commissioner"],
    #     ["ou%3DCIEC-CCIE%2C+o%3DGC%2C+c%3DCA", "Office of the Conflict of Interest and Ethics Commissioner"],
    #     ["ou%3DOCI-BEC%2C+o%3DGC%2C+c%3DCA", "Office of the Correctional Investigator Canada"],
    #     ["ou%3DOIC-CI%2C+o%3DGC%2C+c%3DCA", "Office of the Information Commissioner of Canada"],
    #     ["ou%3DLGHC-LGCC%2C+o%3DGC%2C+c%3DCA", "Office of the Leader of the Government in the House of Commons"],
    #     ["ou%3DOPC-CPVP%2C+o%3DGC%2C+c%3DCA", "Office of the Privacy Commissioner of Canada"],
    #     ["ou%3DOPO-BOA%2C+o%3DGC%2C+c%3DCA", "Office of the Procurement Ombudsman"],
    #     ["ou%3DPSIC-ISPC%2C+o%3DGC%2C+c%3DCA", "Office of the Public Sector Integrity Commissioner of Canada"],
    #     ["ou%3DOSGG-BSGG%2C+o%3DGC%2C+c%3DCA", "Office of the Secretary to the Governor General"],
    #     ["ou%3DSEO-CSE%2C+o%3DGC%2C+c%3DCA", "Office of the Senate Ethics Officer"],
    #     ["ou%3DOSFI-BSIF%2C+o%3DGC%2C+c%3DCA", "Office of the Superintendent of Financial Institutions Canada"],
    #     ["ou%3DOTO-BOC%2C+o%3DGC%2C+c%3DCA", "Office of the Taxpayers' Ombudsman"],
    #     ["ou%3DPPA-APP%2C+o%3DGC%2C+c%3DCA", "Pacific Pilotage Authority Canada"],
    #     ["OU%3DPC-PC%2CO%3DGC%2CC%3DCA", "Parks Canada"],
    #     ["ou%3DPBO-DPB%2Co%3DGC%2Cc%3DCA", "Parliamentary Budget Officer"],
    #     ["ou%3DPBC-CLCC%2C+o%3DGC%2C+c%3DCA", "Parole Board of Canada"],
    #     ["ou%3DPMPRB-CEPMB%2C+o%3DGC%2C+c%3DCA", "Patented Medicine Prices Review Board"],
    #     ["OU%3DPOLAR-POLAIRE%2CO%3DGC%2CC%3DCA", "Polar Knowledge Canada"],
    #     ["ou%3DHorizons-Horizons%2C+o%3DGC%2C+c%3DCA", "Policy Horizons Canada"],
    #     ["ou%3DP3C-P3C%2C+o%3DGC%2C+c%3DCA", "PPP Canada"],
    #     ["ou%3DPMO-CPM%2C+o%3DGC%2C+c%3DCA", "Prime Minister's Office"],
    #     ["ou%3DPCO-BCP%2C+o%3DGC%2C+c%3DCA", "Privy Council Office"],
    #     ["ou%3DPHAC-ASPC%2C+o%3DGC%2C+c%3DCA", "Public Health Agency of Canada"],
    #     ["ou%3DPPSC-SPPC%2C+o%3DGC%2C+c%3DCA", "Public Prosecution Service of Canada"],
    #     ["ou%3DPS-SP%2C+o%3DGC%2C+c%3DCA", "Public Safety Canada"],
    #     ["ou%3DPSDPT-TPFD%2C+o%3DGC%2C+c%3DCA", "Public Servants Disclosure Protection Tribunal Canada"],
    #     ["ou%3DPSC-CFP%2C+o%3DGC%2C+c%3DCA", "Public Service Commission"],
    #     ["OU%3DPSPC-SPAC%2CO%3DGC%2CC%3DCA", "Public Services and Procurement Canada"],
    #     ["ou%3DQFC-CFQ%2C+o%3DGC%2C+c%3DCA", "Quebec Federal Council"],
    #     ["ou%3DRCM-MRC%2C+o%3DGC%2C+c%3DCA", "Royal Canadian Mint"],
    #     ["ou%3DRCMP-GRC%2C+o%3DGC%2C+c%3DCA", "Royal Canadian Mounted Police"],
    #     ["ou%3DRCMPERC-CEEGRC%2C+o%3DGC%2C+c%3DCA", "Royal Canadian Mounted Police External Review Committee"],
    #     ["ou%3DRSC-SRC%2C+o%3DGC%2C+c%3DCA", "Royal Society of Canada, The"],
    #     ["ou%3DRED-DER%2Co%3DGC%2Cc%3DCA", "Rural Economic Development"],
    #     ["ou%3DSIRC-CSARS%2C+o%3DGC%2C+c%3DCA", "Security Intelligence Review Committee"],
    #     ["ou%3DSen-Sen%2C+o%3DGC%2C+c%3DCA", "Senate of Canada"],
    #     ["ou%3DSSC-SPC%2C+o%3DGC%2C+c%3DCA", "Shared Services Canada"],
    #     ["ou%3DSOPF-CIDP%2C+o%3DGC%2C+c%3DCA", "Ship-source Oil Pollution Fund"],
    #     ["ou%3DSSHRC-CRSH%2C+o%3DGC%2C+c%3DCA", "Social Sciences and Humanities Research Council of Canada"],
    #     ["ou%3DSST-TSS%2Co%3DGC%2Cc%3DCA", "Social Security Tribunal of Canada"],
    #     ["ou%3DSCT-TRP%2C+o%3DGC%2C+c%3DCA", "Specific Claims Tribunal"],
    #     ["ou%3DSTCC-CCNO%2C+o%3DGC%2C+c%3DCA", "Standards Council of Canada"],
    #     ["OU%3DSTATCAN-STATCAN%2CO%3DGC%2CC%3DCA", "Statistics Canada"],
    #     ["ou%3DSLS-VMSL%2C+o%3DGC%2C+c%3DCA", "St Lawrence Seaway Management Corporation, The"],
    #     ["ou%3DSCC-CSC%2C+o%3DGC%2C+c%3DCA", "Supreme Court of Canada"],
    #     ["ou%3DTCC-CCI%2C+o%3DGC%2C+c%3DCA", "Tax Court of Canada"],
    #     ["ou%3DTFC-TFC%2C+o%3DGC%2C+c%3DCA", "Telefilm Canada"],
    #     ["ou%3DFBCL-SPFL%2C+o%3DGC%2C+c%3DCA", "The Federal Bridge Corporation Limited"],
    #     ["ou%3DJCCBI-PJCCI%2C+o%3DGC%2C+c%3DCA", "The Jacques Cartier and Champlain Bridges Incorporated"],
    #     ["ou%3DNBC-CCBN%2C+o%3DGC%2C+c%3DCA", "The National Battlefields Commission"],
    #     ["ou%3DTATC-TATC%2C+o%3DGC%2C+c%3DCA", "Transportation Appeal Tribunal of Canada"],
    #     ["ou%3DTSB-BST%2C+o%3DGC%2C+c%3DCA", "Transportation Safety Board of Canada"],
    #     ["ou%3DTC-TC%2C+o%3DGC%2C+c%3DCA", "Transport Canada"],
    #     ["ou%3DTBS-SCT%2C+o%3DGC%2C+c%3DCA", "Treasury Board of Canada Secretariat"],
    #     ["ou%3DVAC-ACC%2C+o%3DGC%2C+c%3DCA", "Veterans Affairs Canada"],
    #     ["ou%3DVRAB-TACC%2C+o%3DGC%2C+c%3DCA", "Veterans Review and Appeal Board"],
    #     ["ou%3DWD-DEO%2C+o%3DGC%2C+c%3DCA", "Western Economic Diversification Canada"],
    #     ["ou%3DWAGE-FEGC%2C+o%3DGC%2C+c%3DCA", "Women and Gender Equality Canada"],
    # ]:
