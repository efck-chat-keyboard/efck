"""
A single module containing all used classes from Qt.
"""
import logging as _logging
import os as _os
import typing as _typing
from importlib import import_module as _import_module

# Specify literally for IDE typing/autocompletion
if _typing.TYPE_CHECKING:
    try:
        from ._qt.pyqt6 import *
    except ImportError:
        try:
            from ._qt.pyside6 import *
        except ImportError:
            try:
                from ._qt.pyqt5 import *
            except ImportError:
                pass

_logger = _logging.getLogger(__name__)

QT_API = _os.environ.get('QT_API', '').lower()  # QtPy uses this variable, so we can too
if QT_API:
    _logger.info('Obeying env variable QT_API="%s"', QT_API)

try_apis = (QT_API,) if QT_API else ('pyqt6', 'pyside6', 'pyqt5')
for qt_api in try_apis:
    try:
        _mod = _import_module(f'.{qt_api}', __package__ + '._qt')
    except ImportError as exc:
        _logger.warning('Failed to import %s: %s: %s', qt_api, exc.__class__.__name__, exc)
    else:
        globals().update(_mod.__dict__)
        QT_API = qt_api
        break

try:
    QApplication
except NameError:
    raise RuntimeError('No importable Qt found. Run `pip install PyQt6` or `pip install PySide6`.') from None


def event_position(event):
    try:
        return event.position()
    except AttributeError:  # PyQt5
        return event.pos()
