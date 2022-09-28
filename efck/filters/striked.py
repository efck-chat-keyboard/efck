example = 'Diagonal strike'


def func(text):
    CH = '\N{combining long solidus overlay}'
    return ''.join(CH + ch for ch in text) + CH
