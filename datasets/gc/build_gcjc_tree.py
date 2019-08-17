# -*- coding: utf-8 -*-
import csv
import re
import traceback
import urllib.parse

GC_OC_FILE='src/gc_job_classifications.tsv'
GR_ENT_FILE='tsv/oc.tsv'
JC_ENT_FILE='tsv/jc.tsv'
CL_ENT_FILE='tsv/cl.tsv'
GR_JC_REL_FILE='tsv/oc_TO_jc.tsv'
JC_JC_REL_FILE='tsv/jc_TO_jc.tsv'
JC_CL_REL_FILE='tsv/jc_TO_cl.tsv'

GC_OC_HDRS = [
    'en_group', 'en_classification', 'en_sub_group',
    'fr_group', 'fr_classification', 'fr_sub_group',
    'pre_1', 'pre_2', 'pre_3', 'min_level', 'max_level',
]
GR_ENT_HDRS = [
    'oc_uid', 'oc_en_name', 'oc_fr_name'
]
JC_ENT_HDRS = [
    'jc_uid', 'jc_en_name', 'jc_fr_name'
]
GR_JC_HDRS = [
    'oc_uid', 'jc_uid'
]
JC_JC_HDRS = [
    's_jc_uid', 'e_jc_uid'
]
JC_CL_HDRS = [
    'jc_uid', 'cl_uid'
]


def load_harvested_list(file_name):
    oc_list = []

    with open(file_name, mode='rt', encoding='utf-8') as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')
        for row in reader:
            row_dict = { k: row[k] for k in GC_OC_HDRS }
            oc_list.append(row_dict)

        return oc_list


def reorganize_classifications(oc_list):
    gr_dict, jc_dict = dict(), dict()

    for row in oc_list:
        min_level, max_level = row['min_level'], row['max_level']
        if not max_level or not min_level:
            continue
        pre_1, pre_2, pre_3 = row['pre_1'], row['pre_2'], row['pre_3']

        en_group, fr_group = row['en_group'], row['fr_group']
        gr_uid = en_group[en_group.find('(')+1:en_group.rfind(')')].strip()
        if gr_uid not in gr_dict:
            gr_dict[gr_uid] = {
                'oc_uid': gr_uid,
                'oc_en_name': en_group[:en_group.find('(')],
                'oc_fr_name': fr_group[:fr_group.find('(')],
                'jc_list': [],
            }
        gr = gr_dict[gr_uid]

        en_class, fr_class = row['en_classification'], row['fr_classification']
        jc_uid = en_class[en_class.find('(')+1:en_class.rfind(')')].strip()
        if '(' in jc_uid:
            jc_uid = jc_uid[jc_uid.find('(')+1:].strip()
        jc_uid = jc_uid.replace(' ', '')
        if jc_uid not in jc_dict:
            jc_dict[jc_uid] = {
                'jc_uid': jc_uid,
                'jc_en_name': en_class[:en_class.find('(')],
                'jc_fr_name': fr_class[:fr_class.find('(')],
                'jc_list': [],
                'cl_list': [],
            }
        jc = jc_dict[jc_uid]
        gr['jc_list'].append(jc_uid)

        if not row['en_sub_group']:
            cl_list = jc['cl_list']
            for pre in [pre_1, pre_2, pre_3]:
                if pre:
                    if '/' not in pre:
                        cl_list.append('%s-%s' % (jc_uid, pre))
                    else:
                        for s in pre.split('/'):
                            if jc_uid != 'FS':
                                cl_list.append('%s-%s' % (jc_uid, s))
                            else:
                                cl_list.append('%s' % s)
            for i in range(int(min_level), int(max_level)+1):
                cl_list.append('%s-%02d' % (jc_uid, i))
            print(gr, jc)
            continue

        en_subgr, fr_subgr = row['en_sub_group'], row['fr_sub_group']
        sg_uid = en_subgr[en_subgr.find('(')+1:en_subgr.rfind(')')].strip()
        if sg_uid not in jc_dict:
            jc_dict[sg_uid] = {
                'jc_uid': sg_uid,
                'jc_en_name': en_subgr[:en_subgr.find('(')],
                'jc_fr_name': fr_group[:fr_group.find('(')],
                'jc_list': [],
                'cl_list': [],
            }
        sc = jc_dict[sg_uid]
        jc['jc_list'].append(sg_uid)

        cl_list = sc['cl_list']
        for pre in [pre_1, pre_2, pre_3]:
            if pre:
                cl_list.append('%s-%s' % (sg_uid, pre))
        for i in range(int(min_level), int(max_level)+1):
            if sg_uid == 'PI-CGC':
                cl_list.append('PI-%d-CGC' % i)
            else:
                cl_list.append('%s-%02d' % (sg_uid, i))

        print(gr, jc, sc)

    return gr_dict, jc_dict


def write_groups(gr_dict, jc_dict):
    with open(GR_ENT_FILE, mode='wt', encoding='utf-8') as tsv_file:
        tsv_file.write('\t'.join(GR_ENT_HDRS) + '\n')
        for key in sorted(gr_dict.keys()):
            item = gr_dict[key]
            row = '\t'.join([item[k] for k in GR_ENT_HDRS]) + '\n'
            tsv_file.write(row)
        print('Wrote %s groups.' % len(gr_dict))

    with open(JC_ENT_FILE, mode='wt', encoding='utf-8') as tsv_file:
        tsv_file.write('\t'.join(JC_ENT_HDRS) + '\n')
        for key in sorted(jc_dict.keys()):
            item = jc_dict[key]
            row = '\t'.join([item[k] for k in JC_ENT_HDRS]) + '\n'
            tsv_file.write(row)
        print('Wrote %s classifications.' % len(jc_dict))

    with open(CL_ENT_FILE, mode='wt', encoding='utf-8') as tsv_file:
        tsv_file.write('cl_uid' + '\n')
        key_set, count = set(), 0
        for key in sorted(jc_dict.keys()):
            for item in sorted(jc_dict[key]['cl_list']):
                row = item + '\n'
                if row in key_set:
                    continue
                key_set.add(row)
                tsv_file.write(row)
                count += 1
        print('Wrote %s classification levels.' % len(jc_dict))

    with open(GR_JC_REL_FILE, mode='wt', encoding='utf-8') as tsv_file:
        tsv_file.write('\t'.join(GR_JC_HDRS) + '\n')
        key_set, count = set(), 0
        for key in sorted(gr_dict.keys()):
            items = gr_dict[key]['jc_list']
            for k in items:
                row = '\t'.join([key, k]) + '\n'
                if row in key_set:
                    continue
                key_set.add(row)
                tsv_file.write(row)
                count += 1
        print('Wrote %s group-classification relations.' % count)

    with open(JC_JC_REL_FILE, mode='wt', encoding='utf-8') as tsv_file:
        tsv_file.write('\t'.join(JC_JC_HDRS) + '\n')
        key_set, count = set(), 0
        for key in sorted(jc_dict.keys()):
            items = jc_dict[key]['jc_list']
            for k in items:
                row = '\t'.join([key, k]) + '\n'
                if row in key_set:
                    continue
                key_set.add(row)
                tsv_file.write(row)
                count +=1
        print('Wrote %s classification relations.' % count)

    with open(JC_CL_REL_FILE, mode='wt', encoding='utf-8') as tsv_file:
        tsv_file.write('\t'.join(JC_CL_HDRS) + '\n')
        key_set, count = set(), 0
        for key in sorted(jc_dict.keys()):
            items = jc_dict[key]['cl_list']
            for k in items:
                row = '\t'.join([key, k]) + '\n'
                if row in key_set:
                    continue
                key_set.add(row)
                tsv_file.write(row)
                count +=1
        print('Wrote %s classification level relations.' % count)


if __name__ == '__main__':
    gc_oc_list = load_harvested_list(GC_OC_FILE)
    print('Loaded %s elements' % len(gc_oc_list))

    oc_gr_dict, oc_cl_dict = reorganize_classifications(gc_oc_list)

    write_groups(oc_gr_dict, oc_cl_dict)
