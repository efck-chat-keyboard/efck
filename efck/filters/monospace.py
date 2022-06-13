import string

_mapping = dict(zip(string.ascii_uppercase +
                    string.ascii_lowercase +
                    string.digits,
                    '𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉'
                    '𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣'
                    '𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿'))

def func(text):
    return ''.join(_mapping.get(ch, ch) for ch in text)
