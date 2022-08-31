
Dev install
-----------
```bash
pip install -e .
pip install PyQt6
# If missing supported emoji fonts, download Noto Color Emoji
scripts/download-emoji-font.sh
```

```shell
grep -PiRIn "\b(TODO|FIXME|HACK)\b|[^\$]\?$" "${@:-.}"
```


Bundling for Windows/MacOS
-------------------------
We use PyInstaller. See [here][deploy-pyqt] for alternatives.

[deploy-pyqt]: https://doc-snapshots.qt.io/qtforpython-6.0/deployment.html

```bash
pip install -e .  # Adds efck/_version.py file
scripts/download-emoji-font.sh
pyinstaller efck-pyi.spec
tree dist
```

Useful links
------------
* https://en.wikipedia.org/wiki/Implementation_of_emojis


Debugging
---------
```bash
gammaray -- python -m efck --debug
# or
python -m efck --debug & gammaray
```


Running bundle in container
---------------------------
Issues with missing:
/usr/lib/x86_64-linux-gnu/libEGL.so.1
mesa-libEGL, mesa-libgl, fontconfig
