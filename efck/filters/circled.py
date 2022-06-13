import string

_mapping = dict(zip(string.ascii_uppercase +
                    string.ascii_lowercase +
                    string.digits,
                    'ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ'
                    'ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ'
                    '⓪①②③④⑤⑥⑦⑧⑨'))


def func(text):
    return ''.join(_mapping.get(ch, ch) for ch in text)

example = 'How cute'
