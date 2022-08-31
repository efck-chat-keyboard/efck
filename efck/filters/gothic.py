import string

example = 'Gothic font'
_mapping = dict(zip(string.ascii_uppercase +
                    string.ascii_lowercase +
                    string.digits,
                    '𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅'
                    '𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟'
                    '𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵'))


def func(text):
    return ''.join(_mapping.get(ch, ch) for ch in text)
