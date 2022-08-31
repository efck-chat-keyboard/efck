import string

example = 'Leetspeak'
_mapping = dict(zip(string.ascii_uppercase +
                    string.ascii_lowercase,
                    '48CD3F9H1JKLMN0PQR57UVWXY2'
                    '48cd3f9h1jklmn0pqr57uvwxy2'))


def func(text):
    return ''.join(_mapping.get(ch, ch) for ch in text)
