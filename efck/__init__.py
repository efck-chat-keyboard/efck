import logging
import sys

from .qt import *


cli_args = []  # Manager. Parsed args will be at 0 index
logger = logging.getLogger(__name__)

if not QApplication.instance():
    qApp = QApplication(sys.argv)
    qApp.setApplicationName('efck-chat-keyboard')
    qApp.setApplicationDisplayName('efck-chat-keyboard')

# Need live qApp before we query platform
assert QApplication.instance()
platform = QGuiApplication.platformName()
IS_MACOS = platform == 'cocoa'
IS_WAYLAND = platform == 'wayland'
IS_WIDOWS = platform == 'windows'
IS_X11 = platform == 'xcb'
logger.info('Qt version: %s, platform: %s', QT_VERSION_STR, platform)

assert QApplication.instance()
CONFIG_DIRS: list[str] = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.AppConfigLocation)
logger.info('Config directories: %s', CONFIG_DIRS)
