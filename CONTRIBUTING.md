
Dev install
-----------
```bash
pip install -e .
# If missing supported emoji fonts, download Noto Color Emoji
scripts/download-emoji-font.sh
```

```shell
grep -PiRIn "\b(TODO|FIXME|HACK)\b|[^\$]\?$" "${@:-.}"
```

Useful links
------------
* https://en.wikipedia.org/wiki/Implementation_of_emojis


Debugging
---------
* `gammaray -- python -m chat-keyboard`
  or `python -m chat-keyboard & gammaray`
