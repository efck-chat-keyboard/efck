from .qt import *
try:
    from ._version import __version__
except ImportError:
    __version__ = '0.0na'

__website__ = 'https://efck-chat-keyboard.github.io'

cli_args = []  # Manager object. Parsed args will be at 0 index

if not QApplication.instance():
    import sys
    qApp = QApplication(sys.argv)
    qApp.setApplicationName('efck-chat-keyboard')
    qApp.setApplicationDisplayName('Efck Chat Keyboard')
    qApp.setApplicationVersion(__version__)

# Need live qApp before we query platform
assert QApplication.instance()
_platform = QGuiApplication.platformName()
IS_MACOS = _platform == 'cocoa'
IS_WAYLAND = _platform == 'wayland'
IS_WIDOWS = _platform == 'windows'
IS_X11 = _platform == 'xcb'

assert QApplication.instance()
CONFIG_DIRS: list[str] = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.AppConfigLocation)
