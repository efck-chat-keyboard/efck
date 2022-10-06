example = 'Diagonal strike'


def func(text):
    CH = '\N{combining long solidus overlay}'
    return ''.join(ch + CH for ch in text)
