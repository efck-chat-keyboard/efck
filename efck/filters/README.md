Filters
=======

Filters (or better called _transforms_) are simple Python modules that define function `func`
(and, optionally, string variable `example`), such as:
```python
def func(text: str) -> str:
    ...
    return transformed_text

example: str = 'Default showcase string when no text'
```

Filters are listed in filename order and are overridden by
respectively named modules in `$XDG_CONFIG_DIR/{app_name}/filters` dir.

Resources
---------
* https://en.wikipedia.org/wiki/Mathematical_Alphanumeric_Symbols
* https://en.wikipedia.org/wiki/Combining_character
* https://yaytext.com
