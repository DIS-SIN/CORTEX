# -*- coding: utf-8 -*-
import csv
import re
import traceback
import urllib.parse

GC_OC_FILE='gc_job_classifications.tsv'
GC_OC_HDRS = [
    'en_group', 'en_classification', 'en_sub_group',
    'fr_group', 'fr_classification', 'fr_sub_group',
    'classification_prefix', 'sub_group_prefix',
    'pre_1', 'pre_2', 'pre_3', 'min_level', 'max_level',
]
GR_ENT_FILE='oc_gr.tsv'
JC_ENT_FILE='oc_jc.tsv'
GR_REL_FILE='oc_gr_TO_oc_gr.tsv'
JC_REL_FILE='oc_jc_TO_oc_jc.tsv'
GR_JC_REL_FILE='oc_gr_TO_oc_jc.tsv'
GR_ENT_HDRS = [
    'uid', 'en_name', 'fr_name'
]
JC_ENT_HDRS = [
    'uid', 'en_name', 'fr_name'
]
REL_HDRS = [
    'parent', 'child'
]
GR_JC_HDRS = [
    'gr_uid', 'jc_uid'
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
    gr_dict, cl_dict = dict(), dict()

    for row in oc_list:
        min_level, max_level = row['min_level'], row['max_level']
        if not max_level or not min_level:
            continue
        classification_prefix = row['classification_prefix']
        sub_group_prefix = row['sub_group_prefix']
        pre_1, pre_2, pre_3 = row['pre_1'], row['pre_2'], row['pre_3']

        en_group, fr_group = row['en_group'], row['fr_group']
        gr_uid = en_group[en_group.find('(')+1:en_group.rfind(')')].strip()
        if gr_uid not in gr_dict:
            gr_dict[gr_uid] = {
                'uid': gr_uid,
                'en_name': en_group[:en_group.find('(')],
                'fr_name': fr_group[:fr_group.find('(')],
                'list': set(),
                'sg_list': set(),
            }
        gr = gr_dict[gr_uid]

        en_class, fr_class = row['en_classification'], row['fr_classification']
        cl_uid = en_class[en_class.find('(')+1:en_class.rfind(')')].strip()
        if cl_uid not in cl_dict:
            cl_dict[cl_uid] = {
                'uid': cl_uid,
                'en_name': en_class[:en_class.find('(')],
                'fr_name': fr_class[:fr_class.find('(')],
                'cl_list': set(),
                'sc_list': set(),
            }
        cl = cl_dict[cl_uid]
        gr['list'].add(cl_uid)

        if not row['en_sub_group']:
            cl_list = cl['cl_list']
            for pre in [pre_1, pre_2, pre_3]:
                if pre:
                    cl_list.add('%s-%s' % (cl_uid, pre))
            for i in range(int(min_level), int(max_level)+1):
                cl_list.add('%s-%02d' % (cl_uid, i))
            continue

        en_subgr, fr_subgr = row['en_sub_group'], row['fr_sub_group']
        sg_uid = en_subgr[en_subgr.find('(')+1:en_subgr.rfind(')')].strip()
        if sg_uid not in gr_dict:
            gr_dict[sg_uid] = {
                'uid': sg_uid,
                'en_name': en_subgr[:en_subgr.find('(')],
                'fr_name': fr_group[:fr_group.find('(')],
                'cl_list': set(),
                'sg_list': set(),
            }
        sg = gr_dict[sg_uid]
        gr['sg_list'].add(sg_uid)

        sc_uid = sg_uid
        if sc_uid not in cl_dict:
            cl_dict[sc_uid] = {
                'uid': sc_uid,
                'en_name': en_subgr[:en_subgr.find('(')],
                'fr_name': fr_group[:fr_group.find('(')],
                'cl_list': set(),
                'sc_list': set(),
            }
        sc = cl_dict[sc_uid]
        sg['list'].add(sc_uid)

        cl_list = sc['cl_list']
        for pre in [pre_1, pre_2, pre_3]:
            if pre:
                cl_list.add('%s-%s' % (sc_uid, pre))
        for i in range(int(min_level), int(max_level)+1):
            cl_list.add('%s-%02d' % (sc_uid, i))
            if sc_uid == 'PI-CGC':
                cl_list.add('PI-%d-CGC' % i)

    return gr_dict, cl_dict


def write_groups(gr_dict):
    with open(GR_ENT_FILE, mode='wt', encoding='utf-8') as tsv_file:
        tsv_file.write('\t'.join(GR_ENT_HDRS) + '\n')
        for key in sorted(gr_dict.keys()):
            item = gr_dict[key]
            row = '\t'.join([item[k] for k in GR_ENT_HDRS]) + '\n'
            tsv_file.write(row)

    with open(GR_REL_FILE, mode='wt', encoding='utf-8') as tsv_file:
        tsv_file.write('\t'.join(REL_HDRS) + '\n')
        for key in sorted(gr_dict.keys()):
            items = gr_dict[key]['sg_list']
            for k in items:
                row = '\t'.join([key, k]) + '\n'
                tsv_file.write(row)

    with open(GR_JC_REL_FILE, mode='wt', encoding='utf-8') as tsv_file:
        tsv_file.write('\t'.join(GR_JC_HDRS) + '\n')
        for key in sorted(gr_dict.keys()):
            items = gr_dict[key]['cl_list']
            for k in items:
                row = '\t'.join([key, k]) + '\n'
                tsv_file.write(row)



def write_relations(row_dict, headers, file_name):
    with open(file_name, mode='wt', encoding='utf-8') as tsv_file:
        tsv_file.write('\t'.join(headers) + '\n')
        for key in sorted(row_dict.keys()):
            item = row_dict[key]
            row = '\t'.join([item[k] for k in headers]) + '\n'
            tsv_file.write(row)


if __name__ == '__main__':
    gc_oc_list = load_harvested_list(GC_OC_FILE)
    print('Loaded %s elements' % len(gc_oc_list))

    oc_gr_dict, oc_cl_dict = reorganize_classifications(gc_oc_list)
