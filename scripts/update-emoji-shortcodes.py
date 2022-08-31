#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import urlopen

# Idea from https://github.com/ikatyang/emoji-cheat-sheet


def emoji_iter():
    with urlopen('https://api.github.com/emojis') as req:
        emojis = json.loads(req.read())
        for name, img_href in emojis.items():
            try:
                emoji_seq = re.search(r'(?<=/unicode/)[^.]+(?=.png)', img_href).group().split('-')
            except Exception:
                # Non-unicode/custom
                print('Ignored non-Unicode:', name, img_href, file=sys.stderr)
                continue
            # Join plain codes, without ZWJ or similar modifiers
            emoji = ''.join(eval(fr'"\U{code:0>8s}"') for code in emoji_seq)
            name = name.replace('_', ' ')
            yield emoji, name


emojis = sorted(emoji_iter())
assert len(emojis) > 100

os.chdir(Path(__file__).parent.parent / 'efck')

with open('emoji-shortcodes.txt', 'w', encoding='utf-8') as fd:
    for emoji, name in emojis:
        print(emoji, name, file=fd)
