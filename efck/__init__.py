from .qt import *
try:
    from ._version import __version__
except ImportError:
    __version__ = '?.?non-installed'


cli_args = []  # Manager. Parsed args will be at 0 index

if not QApplication.instance():
    import sys
    qApp = QApplication(sys.argv)
    qApp.setApplicationName('efck chat keyboard')
    qApp.setApplicationDisplayName('efck chat keyboard')

# Need live qApp before we query platform
assert QApplication.instance()
_platform = QGuiApplication.platformName()
IS_MACOS = _platform == 'cocoa'
IS_WAYLAND = _platform == 'wayland'
IS_WIDOWS = _platform == 'windows'
IS_X11 = _platform == 'xcb'

assert QApplication.instance()
CONFIG_DIRS: list[str] = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.AppConfigLocation)
