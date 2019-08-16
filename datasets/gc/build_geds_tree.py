# -*- coding: utf-8 -*-
import csv
import re
import traceback
import urllib.parse

GC_ORG_ENT_FILE ='gc_org.tsv'
GC_ORG_REL_FILE ='gc_org_TO_gc_org.tsv'

GEDS_ORG_FILE='geds_orgs.tsv'
GEDS_REL_FILE='geds_rels.tsv'

GOC_DEPT_FILE='goc_depts.tsv'

GEDS_ORG_UID = 'org_dn'
GEDS_ORG_HRS = [
    'org_en_name', 'org_fr_name',
    'org_lc_addr', 'org_lc_city', 'org_lc_pr', 'org_lc_pc', 'org_lc_ctry',
]
GEDS_EXT_HRS = [
    'is_dept', 'en_abbr', 'fr_abbr'
]
GOC_DEPT_HRS = [
    'en_name', 'en_url', 'en_abbr',
    'fr_name', 'fr_url', 'fr_abbr',
]
DIFFERENTIATORS = {
    'library', 'vessels',
    'operations', 'atlantic', 'valcartier', 'toronto', 'ottawa', 'suffield'
}
REGEX_REPLACE = [
    { 'regex': re.compile('\(office of the\)', re.UNICODE), 'sub': '' },
    { 'regex': re.compile('office', re.UNICODE), 'sub': '' },
    { 'regex': re.compile(' of canada', re.UNICODE), 'sub': '' },
    { 'regex': re.compile('canadian ', re.UNICODE), 'sub': '' },
    { 'regex': re.compile("'s", re.UNICODE), 'sub': '' },
    { 'regex': re.compile("'", re.UNICODE), 'sub': '' },
    { 'regex': re.compile("\-", re.UNICODE), 'sub': ' ' },
]
IGNORED_WORDS = [
    'of', 'the', 'and', 'for'
]
COMMON_INDEX = 0.85

PARENT_MAPPINGS = {
    'Bank of Canada Museum': 'ou%3DBOC-BDC%2C+o%3DGC%2C+c%3DCA',
    'Blue Water Bridge Canada': 'ou%3DFBCL-SPFL%2C+o%3DGC%2C+c%3DCA',
    'Business Development Bank of Canada': 'ou%3DISED-ISDE%2C+o%3DGC%2C+c%3DCA',
    'Canada Development Investment Corporation': 'ou%3DFIN-FIN%2C+o%3DGC%2C+c%3DCA',
    'Canada Employment Insurance Commission': 'ou%3DESDC-EDSC%2C+o%3DGC%2C+c%3DCA',
    'Canada Firearms Centre': 'ou%3DCFP-PCAF%2C+ou%3DDCSPS-SCSPS%2C+ou%3DRCMP-GRC%2C+o%3DGC%2C+c%3DCA',
    'Canada Infrastructure Bank': 'ou%3DINFC-INFC%2C+o%3DGC%2C+c%3DCA',
    'Canada Lands Company Limited': 'OU%3DPSPC-SPAC%2CO%3DGC%2CC%3DCA',
    'Canada Pension Plan Investment Board': 'ou%3DFIN-FIN%2C+o%3DGC%2C+c%3DCA',
    'Canada Post': 'ou%3DTC-TC%2C+o%3DGC%2C+c%3DCA',
    'Canada Research Chairs':'OU%3DSPIIE-TIPS%2COU%3DRPD-DPR%2COU%3DSSHRC-CRSH%2CO%3DGC%2CC%3DCA',
    'Canadian Accessibility Standards Development Organization': 'ou%3DESDC-EDSC%2C+o%3DGC%2C+c%3DCA',
    'Canadian Race Relations Foundation': 'ou%3DPCH-PCH%2C+o%3DGC%2C+c%3DCA',
    'Canadian Trade Commissioner Service': 'ou%3DGAC-AMC%2CO%3DGC%2CC%3DCA',
    'Crown-Indigenous Relations and Northern Affairs Canada': 'ou%3DISC-SAC%2Co%3DGC%2Cc%3DCA',
    'Environmental Protection Review Canada': 'ou%3DECCC-ECCC%2C+o%3DGC%2C+c%3DCA',
    'Export Development Canada': 'ou%3DGAC-AMC%2CO%3DGC%2CC%3DCA',
    'Freshwater Fish Marketing Corporation': 'ou%3DDFO-MPO%2C+o%3DGC%2C+c%3DCA',
    'Great Lakes Pilotage Authority Canada': 'O%3DGC%2CC%3DCA',
    'Historic Sites and Monuments Board of Canada': 'OU%3DPC-PC%2CO%3DGC%2CC%3DCA',
    'Industrial Technologies Office': 'ou%3DISED-ISDE%2C+o%3DGC%2C+c%3DCA',
    'Judicial Compensation and Benefits Commission': 'ou%3DJUS-JUS%2C+o%3DGC%2C+c%3DCA',
    'Labour Program': 'ou%3DESDC-EDSC%2C+o%3DGC%2C+c%3DCA',
    'Marine Atlantic': 'ou%3DTC-TC%2C+o%3DGC%2C+c%3DCA',
    'Parliament of Canada': 'C%3DCA',
    'Public Sector Pension Investment Board': 'ou%3DTBS-SCT%2C+o%3DGC%2C+c%3DCA',
    'Ridley Terminals Inc.': 'ou%3DTC-TC%2C+o%3DGC%2C+c%3DCA',
    'Royal Military College of Canada': 'OU%3Ddnd-mdn%2CO%3Dgc%2CC%3Dca',
    'Service Canada': 'ou%3DESDC-EDSC%2C+o%3DGC%2C+c%3DCA',
    'VIA Rail Canada': 'ou%3DTC-TC%2C+o%3DGC%2C+c%3DCA',
    'Windsor-Detroit Bridge Authority': 'ou%3DINFC-INFC%2C+o%3DGC%2C+c%3DCA',
}
ABBR_MAPPINGS = {
    'Parliament of Canada': ['PARL', 'PARL'],
    'Canada Research Chairs': ['CHAIRS', 'CHAIRES'],
    'Judicial Compensation and Benefits Commission': ['PGJC', 'JCQC'],
    'Bank of Canada Museum': ['BANKOFCANADAMUSEUM', 'MUSEEDELABANQUEDUCANADA'],
    'Labour Program': ['LABOUR', 'TRAVAIL'],
    'Ridley Terminals Inc.': ['RTI', 'RTI'],
}


def load_geds_orgs(file_name):
    geds_org_dict = dict()

    with open(file_name, mode='rt', encoding='utf-8') as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')
        for row in reader:
            quoted_org_dn = row['org_dn']
            org_dn = urllib.parse.unquote(quoted_org_dn)
            d_pos, c_pos = org_dn.find('-'), org_dn.find(',')

            org_dict = { k: row[k] for k in GEDS_ORG_HRS }
            org_dict.update({
                'is_dept': org_dn.lower().count('ou=') == 1,
                'en_abbr': org_dn[3:d_pos].strip(),
                'fr_abbr': org_dn[d_pos+1:c_pos].strip(),
            })
            geds_org_dict[quoted_org_dn] = org_dict

        return geds_org_dict


def load_goc_deps(file_name):
    goc_dep_dict = dict()

    with open(file_name, mode='rt', encoding='utf-8') as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')
        goc_dep_dict = {
            row['en_name']: {
                k: row[k] if row[k] else None for k in GOC_DEPT_HRS
            }
            for row in reader
        }

    return goc_dep_dict


def extend_entity(entity, dept, ignore=[]):
    for k in GOC_DEPT_HRS:
        if k not in ignore and k in dept and dept[k]:
            entity[k] = dept[k]


def get_words(name):
    n = name.lower()
    for x in REGEX_REPLACE:
        n = x['regex'].sub(x['sub'], n)
    return { w.strip() for w in n.split() if w.lower() not in IGNORED_WORDS }


def match_by_words(dept_dict, dn, org):
    o_name = org['org_en_name']
    if 'word_set' not in org:
        org['word_set'] = get_words(o_name)
        org['word_cnt'] = len(org['word_set'])

    o_name_set, o_cnt = org['word_set'], org['word_cnt']
    for dept_name, dept in dept_dict.items():
        if 'word_set' not in dept:
            dept['word_set'] = get_words(dept['en_name'])
            dept['word_cnt'] = len(dept['word_set'])

        d_name_set, d_cnt = dept['word_set'], dept['word_cnt']
        common_set = o_name_set.intersection(d_name_set)
        if not common_set:
            continue
        union = o_name_set.union(d_name_set).difference(common_set)
        if union.intersection(DIFFERENTIATORS):
            continue

        c_cnt = len(common_set)
        if 2.0 * c_cnt > COMMON_INDEX * (d_cnt + o_cnt):
            if all([c == ' ' or c.isupper() for c in o_name]):
                org['org_en_name'] = dept_name
            return True, dept_name

    return False, None


def match_by_name(dept_dict, dn, org):
    o_name = org['org_en_name']

    dept_name = o_name
    if dept_name in dept_dict:
        return True, o_name

    dept_name = o_name + ' (Department of)'
    if dept_name in dept_dict:
        return True, dept_name

    dept_name = o_name + ' of Canada'
    if dept_name in dept_dict:
        return True, dept_name

    dept_name = o_name + ' Canada'
    if dept_name in dept_dict:
        return True, dept_name

    if o_name.startswith('Office of the'):
        dept_name = o_name[len('Office of the'):].strip() + ' (Office of the)'
        if dept_name in dept_dict:
            return True, dept_name

        dept_name = o_name[len('Office of the'):].strip() + ' Canada (Office of the)'
        if dept_name in dept_dict:
            return True, dept_name

    if o_name.endswith(', Office of the'):
        dept_name = o_name[0:len(o_name)-len(', Office of the'):].strip() + ' (Office of the)'
        if dept_name in dept_dict:
            return True, dept_name

    if o_name.endswith('Research Council of Canada'):
        dept_name = o_name[0:len(o_name)-len('Research Council of Canada'):].strip() + ' Research Canada'
        if dept_name in dept_dict:
            return True, dept_name

    if o_name.startswith('Office of the Commissioner, '):
        dept_name = o_name[len('Office of the Commissioner, '):].strip()
        if dept_name in dept_dict:
            return True, dept_name

    if o_name.startswith('Federal Public Sector'):
        dept_name = 'Public Service ' + o_name[len('Federal Public Sector'):].strip()
        if dept_name in dept_dict:
            return True, dept_name

    if o_name == 'Canadian Tourism Commission':
        dept_name = 'Destination Canada'
        if dept_name in dept_dict:
            org['org_en_name'] = dept_name
            return True, dept_name

    if dn == 'ou%3DOMBUDSMAN-OMBUDSMAN%2COU%3DDND-MDN%2CO%3DGC%2CC%3DCA':
        dept_name = 'Ombudsman for the Department of National Defence and the Canadian Forces (Office of the)'
        if dept_name in dept_dict:
            org['org_en_name'] = dept_name
            return True, dept_name

    return False, None


def update_depts(matches, dept_dict):
    print('Matches = %s' % len(matches))

    for dept_name in sorted(matches.keys()):
        org = matches[dept_name]
        print('[%s] %s -> [%s] %s' % (
            dept_name, dept_dict[dept_name]['en_abbr'],
            org['org_en_name'], org['en_abbr']
        ))
        dept_dict.pop(dept_name)


def match_depts(dept_dict, geds_dict, match_func):
    matches = dict()

    for dn, org in geds_dict.items():
        is_match, dept_name = match_func(dept_dict, dn, org)
        if is_match:
            org['org_fr_name'] = dept_dict[dept_name]['fr_name']
            extend_entity(org, dept_dict[dept_name], ignore=['en_name', 'fr_name'])
            matches[dept_name] = org

    update_depts(matches, dept_dict)


def show_remaining_depts(dept_dict, details=False):
    print('Remains = %s' % len(dept_dict))
    if not details:
        return

    for k in sorted(dept_dict.keys()):
        print('--- %s %s' % (k, dept_dict[k]['en_abbr']))


if __name__ == '__main__':
    geds_org_dict = load_geds_orgs(GEDS_ORG_FILE)
    print('Loaded %d orgs by org_dn.' % len(geds_org_dict))

    goc_dep_dict = load_goc_deps(GOC_DEPT_FILE)
    print('Loaded %d deps by [en] name.' % len(goc_dep_dict))

    match_depts(goc_dep_dict, geds_org_dict, match_by_name)
    show_remaining_depts(goc_dep_dict, True)

    match_depts(goc_dep_dict, geds_org_dict, match_by_words)
    show_remaining_depts(goc_dep_dict, True)

    ent_file = open(GC_ORG_ENT_FILE, mode='wt', encoding='utf-8')
    ent_file.write('\t'.join([GEDS_ORG_UID] + GEDS_ORG_HRS + GEDS_EXT_HRS) + '\n')
    for dn, org in geds_org_dict.items():
        row = '\t'.join([dn] + ["%s" % org[k] if k in org else "" for k in GEDS_ORG_HRS + GEDS_EXT_HRS]) + '\n'
        ent_file.write(row)

    rel_file = open(GC_ORG_REL_FILE, mode='wt', encoding='utf-8')
    with open(GEDS_REL_FILE, mode='rt', encoding='utf-8') as text_file:
        for line in text_file.readlines():
            rel_file.write(line)

    for dept_name, dept in goc_dep_dict.items():
        org = dict()
        o_name = dept['en_name']
        org['org_en_name'] = o_name
        org['org_fr_name'] = dept['fr_name']
        extend_entity(org, dept, ignore=['en_name', 'fr_name'])
        org['is_dept'] = False
        if o_name in ['Parliament of Canada', 'Great Lakes Pilotage Authority Canada']:
            org['is_dept'] = True
        if 'en_abbr' not in org or not org['en_abbr']:
            org['en_abbr'], org['fr_abbr'] = ABBR_MAPPINGS[org['org_en_name']]

        parent_org_dn = urllib.parse.unquote(PARENT_MAPPINGS[o_name])
        child_org_dn = 'ou=%s-%s,%s' % (org['en_abbr'], org['fr_abbr'], parent_org_dn)
        org['org_dn'] = urllib.parse.quote(child_org_dn)

        row = '\t'.join([org['org_dn']] + ["%s" % org[k] if k in org else "" for k in GEDS_ORG_HRS + GEDS_EXT_HRS]) + '\n'
        ent_file.write(row)

        row = '\t'.join([PARENT_MAPPINGS[o_name], org['org_dn']]) + '\n'
        rel_file.write(row)

    ent_file.close()
    rel_file.close()
