Bugs
----
Please report bugs with sufficient details and steps that,
if followed, reliably reproduce the issue.
Please see [how to report bugs effectively][bugs].

Ensure your bug is reproducible with the latest version,
ideally git master.
If applicable, please attach debug log as output by:

```shell
    efck-chat-keyboard --debug
    # or
    python -m efck --debug
```

[bugs]: https://www.chiark.greenend.org.uk/~sgtatham/bugs.html


Contributing code / PRs
-----------------------
Contributing pull requests is welcomed. A good place to find issues
to fix is the issue tracker, such as the bugs reported. Also sometimes
the following command line:

```shell
grep -RIPin "\b(TODO|FIXME|HACK|XXX)\b|[^\$]\?$" "${@:-.}"
```


Custom tabs, custom filters
---------------------------
To cook own tabs, extend
[`efck.tab.Tab`](https://github.com/efck-chat-keyboard/efck/blob/master/efck/tab.py)
in your own file, saved at a platform-dependent
[`AppConfigLocation`](https://doc.qt.io/qt-6/qstandardpaths.html#StandardLocation-enum):
`{AppConfigLocation}/tabs/{your_tab}.py`.

To cook own text transforms, save files containing
`func(text: str) -> str` (see built-in examples)
into `{AppConfigLocation}/filters/{your_transform}.py`.


Dev installation
----------------
```shell
pip install -e '.[extra]'
pip install PyQt6  # or PySide6, or PyQt5
# Optional, if missing an emoji font. Most platforms supply own
# emoji fonts and might not yet support rendering Noto Color Emoji.
scripts/download-emoji-font.sh
```


Testing
-------
```shell
QT_API=pyqt6  # export to force use of specific Qt bindings
python -m efck.tests -v
python -m efck --debug
```


Bundling for macOS/Widows
-------------------------
See relevant commands in the [CI workflow](https://github.com/efck-chat-keyboard/efck/search?l=YAML&q=pyinstaller).


Debugging
---------
```shell
gammaray -- python -m efck --debug
# or
python -m efck --debug & gammaray
```
And, of course, [your IDE](https://www.jetbrains.com/help/pycharm/part-1-debugging-python-code.html).

Resources
---------
* https://en.wikipedia.org/wiki/Implementation_of_emojis
