# -*- coding: utf-8 -*-
import csv
import re
import traceback
import urllib.parse

GCJC_ORG_FILE='gc_jc.tsv'
GCJC_REL_FILE='gc_jc_TO_gc_jc.tsv'

GC_JC_COL_FILE='gc_job_classifications.tsv'

GC_JC_COLL_HRS = [
    'en_group', 'en_classification', 'en_sub_group',
    'fr_group', 'fr_classification', 'fr_sub_group',
    'classification_prefix', 'sub_group_prefix',
    'pre_1', 'pre_2', 'pre_3', 'min_level', 'max_level',
]


def load_harvested_gc_jc(file_name):
    jc_list = []

    with open(file_name, mode='rt', encoding='utf-8') as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')
        for row in reader:
            org_dict = { k: row[k] for k in GC_JC_COLL_HRS }
            jc_list.append(org_dict)

        return jc_list


if __name__ == '__main__':
    gc_jc_list = load_harvested_gc_jc(GC_JC_COL_FILE)
    print('Loaded %s elements' % len(gc_jc_list))
