import os as _os
from importlib import import_module as _import_module

QT_API = _os.environ.get('QT_API')  # QtPy honors this variable, so we can too
if QT_API in ('pyqt6', 'pyside6', 'pyqt5'):
    _mod = _import_module(f'.{QT_API}', __package__ + '._qt')
    globals().update(_mod.__dict__)
else:
    try:
        from ._qt.pyqt6 import *
        QT_API = 'pyqt6'
    except ImportError:
        try:
            from ._qt.pyside6 import *
            QT_API = 'pyside6'
        except ImportError:
            try:
                from ._qt.pyqt5 import *
                QT_API = 'pyqt5'
            except ImportError:
                try:
                    from ._qt.qtpy import *
                    from qtpy import API_NAME as QT_API
                except ImportError:
                    pass
try:
    QApplication
except NameError:
    raise RuntimeError('No importable Qt found. Run `pip install PyQt6` or `pip install PySide6`.') from None
