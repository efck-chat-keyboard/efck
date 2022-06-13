import string


_mapping = dict(zip(string.ascii_uppercase +
                    string.ascii_lowercase +
                    string.digits +
                    '!?',
                    # TODO: use better M than W, e.g. ꟽ
                    '∀qƆpƎℲפHIſʞ˥WNOԀQɹS┴∩ΛMX⅄Z'
                    'ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz'
                    '0ƖᄅƐㄣϛ9ㄥ86'
                    '¡¿'))


def func(text):
    return ''.join(_mapping.get(ch, ch) for ch in reversed(text))


example = 'Fifth house'
