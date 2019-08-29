import hashlib
import json
import sys

def get_md5(text):
    m = hashlib.md5()
    m.update(text.encode())
    return m.hexdigest()


def get_content(file_name):
    text = ''
    with open(file_name, mode='rt', encoding='utf-8') as text_file:
        for line in text_file.readlines():
            text += line
    return text


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 verify_response_set.py <template> <response>")
        exit(1)

    file_name = sys.argv[1]
    t_json = json.loads(get_content(file_name))
    template = dict({
        'uid': t_json['uid'],
        'title': [t_json['title']['en'], t_json['title']['fr']],
        'description': [t_json['description']['en'], t_json['description']['fr']],
        'valid': [t_json['valid']['from'], t_json['valid']['to']],
        'version': t_json['version'],
        'questions': dict()
    })
    for cq in t_json['questions']:
        if cq['qid'] == 'none':
            continue
        qid = cq['cortex']['uid']
        if qid not in template:
            template['questions'][qid] = dict()
        q = template['questions'][qid]
        q['type'] = cq['cortex']['questionType']
        q['question'] = [cq['question']['en'], cq['question']['fr']]
        q['classified_as'] = cq['cortex']['classifiedAs']
        q['options'] = json.dumps(cq['options'])

    for k in sorted(template.keys()):
        print(k, template[k])

    stats, total = dict(), 0
    file_name = sys.argv[2]
    r_json = json.loads(get_content(file_name))
    response = dict({
        'total': 0,
        'data': dict()
    })
    data = response['data']

    for r in r_json:
        response['total'] += 1

        for question in r['questions']:
            qid = question['uid']
            q = template['questions'][qid]
            if qid not in data:
                data[qid] = dict({
                    'type': q['type'],
                    'total': 0,
                    'stats': dict()
                })
            stats = data[qid]['stats']
            ans = question['questionAnswer']
            if q['type'] != 'CLASSIFIED':
                cqt = question['questionType']
                if cqt in ['SINGLE_CHOICE', 'FREE_TEXT']:
                    stats[ans] = stats.get(ans, 0) + 1
                if cqt == 'MULTI_CHOICE':
                    answers = []
                    if isinstance(ans, str):
                        answers = [ans]
                    else:
                        if isinstance(ans, list):
                            answers = ans
                    if not answers:
                        print('DATA ERROR [%s] %s' % (total, question))
                        continue
                    for answer in answers:
                        stats[ans] = stats.get(ans, 0) + 1
            if q['classified_as'] in ['GC_Language', 'GC_ClsLvl', 'GC_Org', 'CP_CSD']:
                stats[ans] = stats.get(ans, 0) + 1

            data[qid]['total'] += 1


    for k, v in response.items():
        if k != 'data':
            print(k, v)
        else:
            for k1, v1 in data.items():
                print('\t', k1, v1, sum(v1['stats'].values()))
