import re
import sys

REGEX = re.compile(r'\s{2,}', re.UNICODE)


def get_options(file_name):
    option_dict = dict()
    option_name, option_text = None, ''
    with open(file_name, mode='rt', encoding='utf-8') as text_file:
        for line in text_file.readlines():
            if line.startswith('>>>'):
                option_name = line.strip('\n')[3:]
                continue
            if line.startswith('<<<'):
                if option_name:
                    option_dict[option_name] = REGEX.sub(' ', option_text.strip())
                    option_name, option_text = None, ''
                continue
            if option_name:
                option_text += line.replace('\n', ' ')
        return option_dict


def get_template(file_name):
    text = ''
    with open(file_name, mode='rt', encoding='utf-8') as text_file:
        for line in text_file.readlines():
            text += line
    return text


def write_file(file_name, text):
    with open(file_name, mode='wt', encoding='utf-8') as text_file:
        text_file.write(text)


if __name__ == '__main__':
    template = get_template('sink.avro.neo4j.json.template')
    option_dict = get_options('sink_cyphers.cql')
    for k, v in option_dict.items():
        template = template.replace('{%s}' % k, v)
    write_file('sink.avro.neo4j.json', template)
