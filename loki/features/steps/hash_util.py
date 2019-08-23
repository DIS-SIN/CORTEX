import hashlib
import sys


def get_content(file_name):
    text = ''
    with open(file_name, mode='rt', encoding='utf-8') as text_file:
        for line in text_file.readlines():
            text += line
    return text


def get_md5(text):
    m = hashlib.md5()
    m.update(text.encode())
    return m.hexdigest()


def get_sha256(text):
    m = hashlib.sha256()
    m.update(text.encode())
    return m.hexdigest()


def get_file_md5(file_name):
    return get_md5(get_content(file_name))


def get_file_sha256(file_name):
    return get_sha256(get_content(file_name))


if __name__ == '__main__':
    print('md5', get_file_md5(sys.argv[1]))
    print('sha256', get_file_sha256(sys.argv[1]))
