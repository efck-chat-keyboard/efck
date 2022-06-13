"""
Based on:
https://github.com/jmdaemon/sapply/blob/master/src/sapply/zalgo.py
view-source:https://web.archive.org/web/20120929234533/http://str.blogsite.org/Zalgo.htm
"""
from random import choice, randrange

ZALGO_UP = list(
    '\u030d\u030e\u0304\u0305'  # ̍ ̎ ̄ ̅
    '\u033f\u0311\u0306\u0310'  # ̿ ̑ ̆ ̐
    '\u0352\u0357\u0351\u0307'  # ͒ ͗ ͑ ̇
    '\u0308\u030a\u0342\u0343'  # ̈ ̊ ͂ ̓
    '\u0344\u034a\u034b\u034c'  # ̈́ ͊ ͋ ͌
    '\u0303\u0302\u030c\u0350'  # ̃ ̂ ̌ ͐
    '\u0300\u0301\u030b\u030f'  # ̀ ́ ̋ ̏
    '\u0312\u0313\u0314\u033d'  # ̒ ̓ ̔ ̽
    '\u0309\u0363\u0364\u0365'  # ̉ ͣ ͤ ͥ
    '\u0366\u0367\u0368\u0369'  # ͦ ͧ ͨ ͩ
    '\u036a\u036b\u036c\u036d'  # ͪ ͫ ͬ ͭ
    '\u036e\u036f\u033e\u035b'  # ͮ ͯ ̾ ͛
    '\u0346\u031a'              # ͆ ̚
)
ZALGO_MID = list(
    '\u0315\u031b\u0340\u0341'  # ̕ ̛  ̀ ́
    '\u0358\u0321\u0322\u0327'  # ͘ ̡  ̢ ̧
    '\u0328\u0334\u0335\u0336'  # ̨ ̴  ̵ ̶
    '\u034f\u035c\u035d\u035e'  # ͏ ͜  ͝ ͞
    '\u035f\u0360\u0362\u0338'  # ͟ ͠  ͢ ̸
    '\u0337\u0361'              # ̷ ͡
)
SPACE_MID = ZALGO_MID + list(
    '\u0488\u0489'              # ҈ ҉
)
ZALGO_DOWN = list(
    '\u0316\u0317\u0318\u0319'  # ̖ ̗  ̘ ̙
    '\u031c\u031d\u031e\u031f'  # ̜ ̝  ̞ ̟
    '\u0320\u0324\u0325\u0326'  # ̠ ̤  ̥ ̦
    '\u0329\u032a\u032b\u032c'  # ̩ ̪  ̫ ̬
    '\u032d\u032e\u032f\u0330'  # ̭ ̮  ̯ ̰
    '\u0331\u0332\u0333\u0339'  # ̱ ̲  ̳ ̹
    '\u033a\u033b\u033c\u0345'  # ̺ ̻  ̼ ͅ
    '\u0347\u0348\u0349\u034d'  # ͇ ͈  ͉ ͍
    '\u034e\u0353\u0354\u0355'  # ͎ ͓  ͔ ͕
    '\u0356\u0359\u035a\u0323'  # ͖ ͙  ͚  ̣
)


def zalgo(text):
    out = []
    for ch in text:
        out.append(ch)
        out.extend(choice(ZALGO_UP) for _ in range(randrange(3)))
        out.extend(choice(ZALGO_DOWN) for _ in range(randrange(4)))
        out.extend(choice(SPACE_MID if ch == ' ' else ZALGO_MID) for _ in range(randrange(2)))
    return ''.join(out)


func = zalgo
example = 'Zalgo text'