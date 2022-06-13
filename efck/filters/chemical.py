"""
Idea source: https://github.com/jwilk/chemiscripts
"""
import re
import string

_subscript_mapping = dict(zip(string.digits, '₀₁₂₃₄₅₆₇₈₉'))
_superscript_mapping = dict(zip(string.digits + '+-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻'))

def _subscript(m):
    return ''.join(_subscript_mapping[ch] for ch in m.group().strip())

def _superscript(m):
    return ''.join(_superscript_mapping[ch] for ch in m.group().strip())


def func(text):
    '3(NH4)2S + Sb2S5 -> 6NH4+ + 2SbS4 3+'
    text = re.sub(r'(?<=[\w)])\d+', _subscript, text)
    text = re.sub(r'\b\s+\d+(?![\w(])', _superscript, text)
    text = re.sub(r'(?<! )[+-](?!\w)', _superscript, text)
    text = text.replace('->', '→')
    return text


example = '3(NH4)2S + Sb2S5 -> 6NH4+ + 2SbS4 3+'
assert func(example) == '3(NH₄)₂S + Sb₂S₅ → 6NH₄⁺ + 2SbS₄³⁺'
example = 'CO2 + 2H2O+ ->'
