import argparse
import logging
import sys

from . import CONFIG_DIRS, cli_args
from .qt import QApplication, QT_VERSION_STR

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        prog='efck-chat-keyboard',
        description='''Emoji filter / Unicode chat keyboard.
        A Qt GUI chat tool that pops up a dialog with tabs for:
        emoji filtering / selection,
        text to fancy Unicode transformation,
        GIF meme selection etc. (extensible architecture).
        Upon activation, it 'pastes' your selection into the previously active
        (focused) window, such as a web browser or a desktop chat app or similar.
        ''')
    parser.add_argument('--force-clipboard', action='store_true',
                        help='Copy the emoji/text into clipboard in addition to typing it out. '
                             "Useful if typeout doesn't work.")
    parser.add_argument('--debug', action='store_const', dest='log_level', const=logging.DEBUG,
                        default=logging.ERROR, help='Print debug messages to stderr')
    args = parser.parse_args()
    cli_args[:] = [args]
    logging.basicConfig(format='{relativeCreated:.0f}\t{levelname:8s}\t{name:15s}\t{message}',
                        style='{',
                        level=args.log_level)


def main():
    parse_args()

    logger.info('Qt version: %s, platform: %s', QT_VERSION_STR, QApplication.platformName())
    logger.info('Config directories: %s', CONFIG_DIRS)

    from .gui import MainWindow
    from .config import load_config

    load_config()
    window = MainWindow()
    window.show()
    sys.exit(QApplication.instance().exec())


main()
