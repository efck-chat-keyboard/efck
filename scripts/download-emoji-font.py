#!/usr/bin/env python3
from pathlib import Path
from urllib.request import urlopen

DIR = Path(__file__).parent.parent / 'efck'

# See: https://github.com/googlefonts/noto-emoji/pull/323
URL = 'https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji_WindowsCompatible.ttf'
with urlopen(URL) as resp, \
        open(DIR / 'NotoColorEmoji.ttf', 'wb') as out:
    out.write(resp.read())
