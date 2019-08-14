# -*- coding: utf-8 -*-
import csv
import traceback
import urllib.parse

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

# DIRECT_MAPPINGS = {
#     'Ombudsman for the Department of National Defence and the Canadian Forces (Office of the)': ['Ombudsman': 'ou%3DOMBUDSMAN-OMBUDSMAN%2COU%3DDND-MDN%2CO%3DGC%2CC%3DCA'],
# }
#
# Natural Sciences and Engineering Research Canada NSERC
# Public Service Labour Relations and Employment Board PSLREB
#
# PARENT_MAPPINGS = {
#     'Bank of Canada Museum': ['Bank of Canada', 'ou%3DBOC-BDC%2C+o%3DGC%2C+c%3DCA'],
#     'Blue Water Bridge Canada': ['The Federal Bridge Corporation Limited', 'ou%3DFBCL-SPFL%2C+o%3DGC%2C+c%3DCA'],
#     'Business Development Bank of Canada': ['Innovation, Science and Economic Development Canada', 'ou%3DISED-ISDE%2C+o%3DGC%2C+c%3DCA'],
#     'Canada Development Investment Corporation': ['Finance Canada', 'ou%3DFIN-FIN%2C+o%3DGC%2C+c%3DCA'],
#     'Canada Employment Insurance Commission': ['Employment and Social Development Canada', 'ou%3DESDC-EDSC%2C+o%3DGC%2C+c%3DCA'],
#     'Canada Firearms Centre': ['CANADIAN FIREARMS PROGRAM', 'ou%3DCFP-PCAF%2C+ou%3DDCSPS-SCSPS%2C+ou%3DRCMP-GRC%2C+o%3DGC%2C+c%3DCA	CANADIAN FIREARMS PROGRAM'],
#     'Canada Infrastructure Bank': ['Infrastructure Canada', 'ou%3DINFC-INFC%2C+o%3DGC%2C+c%3DCA'],
#     'Canada Lands Company Limited': ['Public Services and Procurement Canada', 'OU%3DPSPC-SPAC%2CO%3DGC%2CC%3DCA'],
#     'Canada Pension Plan Investment Board': ['Finance Canada', 'ou%3DFIN-FIN%2C+o%3DGC%2C+c%3DCA'],
#     'Canada Post': ['Transport Canada', 'ou%3DTC-TC%2C+o%3DGC%2C+c%3DCA'],
#     'Canada Research Chairs': ['Tri-agency Institutional Programs Secretariat', 'OU%3DSPIIE-TIPS%2COU%3DRPD-DPR%2COU%3DSSHRC-CRSH%2CO%3DGC%2CC%3DCA'],
#     'Canadian Accessibility Standards Development Organization': ['Employment and Social Development Canada', 'ou%3DESDC-EDSC%2C+o%3DGC%2C+c%3DCA'],
#     'Canadian Coast Guard': ['Office of the Commissioner, Canadian Coast Guard', 'ou%3DCOMMCCG-COMMGCC%2C+ou%3DDM-SM%2C+ou%3DDFO-MPO%2C+o%3DGC%2C+c%3DCA'],
#     'Canadian Race Relations Foundation': ['Canadian Heritage', 'ou%3DPCH-PCH%2C+o%3DGC%2C+c%3DCA'],
#     'Canadian Trade Commissioner Service': ['Global Affairs Canada', 'ou%3DGAC-AMC%2CO%3DGC%2CC%3DCA'],
#     'Crown-Indigenous Relations and Northern Affairs Canada': ['Indigenous Services Canada', 'ou%3DISC-SAC%2Co%3DGC%2Cc%3DCA'],
#     'Historic Sites and Monuments Board of Canada': ['Parks Canada', 'OU%3DPC-PC%2CO%3DGC%2CC%3DCA'],
#     'Industrial Technologies Office': ['Innovation, Science and Economic Development Canada', 'ou%3DISED-ISDE%2C+o%3DGC%2C+c%3DCA'],
#     'Judicial Compensation and Benefits Commission': ['Justice Canada', 'ou%3DJUS-JUS%2C+o%3DGC%2C+c%3DCA'],
#     'Labour Program': ['Employment and Social Development Canada', 'ou%3DESDC-EDSC%2C+o%3DGC%2C+c%3DCA'],
#     'Royal Military College of Canada': ['National Defence', 'OU%3Ddnd-mdn%2CO%3Dgc%2CC%3Dca'],
#     'Service Canada': ['Employment and Social Development Canada', 'ou%3DESDC-EDSC%2C+o%3DGC%2C+c%3DCA'],
#     'Superintendent of Bankruptcy Canada (Office of the)': ['Innovation, Science and Economic Development Canada', 'ou%3DISED-ISDE%2C+o%3DGC%2C+c%3DCA'],
# }
#
# REVERSE_MAPPINGS = {
#     'Destination Canada': 'Canadian Tourism Commission',
# }
#
# NEW_MAPPINGS = [
#     'Environmental Protection Review Canada',
#     'Export Development Canada',
#     'Freshwater Fish Marketing Corporation',
#     'Great Lakes Pilotage Authority Canada',
#     'Marine Atlantic',
#     'Parliament of Canada',
#     'Public Sector Pension Investment Board',
#     'Ridley Terminals Inc.',
#     'VIA Rail Canada',
#     'Windsor-Detroit Bridge Authority',
# ]

def load_geds_orgs(file_name):
    geds_org_dict, geds_en_abr_dict = dict(), dict()

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

            if org_dict['is_dept']:
                geds_en_abr_dict[org_dict['en_abbr']] = row['org_en_name']

        return geds_org_dict, geds_en_abr_dict


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


def get_words(name):
    n = name.lower()
    n = n.replace(', office of the', '')
    n = n.replace('(office of the)', '').replace('office', '')
    n = n.replace('of canada', '').replace('canadian', '')
    n = n.replace("'s", ' ').replace("'", ' ').replace("-", ' ')
    r = {
        w.strip()
        for w in n.split()
        if w.lower() not in ['of', 'the', 'and']
    }
    return r


def match_by_words(dept_dict, dn, org):


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
            matches[dept_name] = org

    update_depts(matches, dept_dict)


def show_remaining_depts(dept_dict, details=False):
    print('Remains = %s' % len(dept_dict))
    if not details:
        return

    for k in sorted(dept_dict.keys()):
        print('--- %s %s' % (k, dept_dict[k]['en_abbr']))


if __name__ == '__main__':
    geds_org_dict, geds_en_abr_dict = load_geds_orgs(GEDS_ORG_FILE)
    print('Loaded %d orgs by org_dn.' % len(geds_org_dict))
    print('Loaded %d deps by [en] abbr.' % len(geds_en_abr_dict))

    goc_dep_dict = load_goc_deps(GOC_DEPT_FILE)
    print('Loaded %d deps by [en] name.' % len(goc_dep_dict))

    print(match_by_name)
    match_depts(goc_dep_dict, geds_org_dict, match_by_name)
    show_remaining_depts(goc_dep_dict, True)

    # dep_name_dict = { k: get_words(k) for k in goc_en_dep_dict.keys() }
    # common_en_mix_names = dict()
    # for _, org in geds_org_dict.items():
    #     o_name = org['org_en_name']
    #     if o_name in common_en_dept_names or o_name in common_en_org_names:
    #         continue
    #
    #     o_name_set = get_words(o_name)
    #     o_cnt = len(o_name_set)
    #     for d_name, d_name_set in dep_name_dict.items():
    #         common = o_name_set.intersection(d_name_set)
    #         if not common:
    #             continue
    #         union = o_name_set.union(d_name_set).difference(common)
    #         if union.intersection(DIFFERENTIATORS):
    #             continue
    #
    #         c_cnt = len(common)
    #         d_cnt = len(d_name_set)
    #         if 2.0 * c_cnt > 0.85 * (d_cnt + o_cnt):
    #             if all([c == ' ' or c.isupper() for c in o_name]):
    #                 org['org_en_name'] = d_name
    #             if goc_en_dep_dict[d_name]:
    #                 org['en_abbr'] = goc_en_dep_dict[d_name]
    #             common_en_mix_names[d_name] = org
    #             break
    #
    # print('common_en_mix_names = %s' % len(common_en_mix_names))
    # for d_name in sorted(common_en_mix_names.keys()):
    #     org = common_en_mix_names[d_name]
    #     print('%s %s -> %s %s' % (d_name, goc_en_dep_dict[d_name], org['org_en_name'], org['en_abbr']))
    #     goc_en_dep_dict.pop(d_name)
    # print('remains = %s' % len(goc_en_dep_dict))
    #
