import string

_mapping = dict(zip(string.ascii_uppercase +
                    string.ascii_lowercase +
                    string.digits,
                    '𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭'
                    '𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇'
                    '𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵'))


def func(text):
    return ''.join(_mapping.get(ch, ch) for ch in text)

example = 'Bold face'
