import string

_mapping = dict(zip(string.ascii_uppercase +
                    string.ascii_lowercase +
                    '?',
                    'π°π±π²π³π΄π΅πΆπ·πΈπΉπΊπ»πΌπ½πΎπΏππππππππππ'
                    'π°π±π²π³π΄π΅πΆπ·πΈπΉπΊπ»πΌπ½πΎπΏππππππππππ'
                    'π―'))


def func(text):
    return ''.join(_mapping.get(ch, ch) for ch in text)
