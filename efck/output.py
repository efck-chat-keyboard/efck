import logging
import os
import shutil
import subprocess
from tempfile import NamedTemporaryFile

from . import IS_X11, IS_WAYLAND, IS_WIDOWS, _platform
from .qt import *

logger = logging.getLogger(__name__)


def type_chars(text: str, force_clipboard):
    TYPEOUT_COMMANDS = (
        (IS_X11, ['xdotool', 'type', text]),
        (IS_X11 or IS_WAYLAND, ['ydotool', 'type', '--next-delay', '0', '--key-delay', '0', text]),
        # Defer to _copy_to_clipboard
        # (IS_MACOS, ['osascript', '-e', _OSASCRIPT.format(text.replace('"', '\\"'))]),
        (IS_X11 or IS_WAYLAND, ['wtype', text]),
        (IS_WIDOWS, lambda: _type_windos(text))
    )
    once = False
    res = -1  # 0/Falsy = success
    for cond, args in TYPEOUT_COMMANDS:
        if cond:
            if not once:
                logger.info('Typing out text: %s', text)
                once = True

            if callable(args):
                res = args()
                break

            if not shutil.which(args[0]):
                logger.warning('Platform "%s" but command "%s" unavailable', _platform, args[0])
                continue
            logger.info('Executing: %s', ' '.join(args))
            proc = subprocess.run(args)
            res = proc.returncode
            if not res:
                break
            logger.warning('Subprocess exit code/error: %s', res)
    else:
        logger.error('No command applies. Please see above for additional warnings.')

    if res == 0 and not force_clipboard:
        # Supposedly we're done
        return

    # Otherwise
    _copy_to_clipboard(text)


# https://apple.stackexchange.com/questions/171709/applescript-get-active-application
# https://stackoverflow.com/questions/41673019/insert-emoji-into-focused-text-input
# https://stackoverflow.com/questions/60385810/inserting-chinese-characters-in-applescript
# https://apple.stackexchange.com/questions/288536/is-it-possible-to-keystroke-special-characters-in-applescript
_OSASCRIPT = '''
set the clipboard to "{}"
tell application "System Events" to keystroke "v" using command down
'''


def _copy_to_clipboard(text):
    # Copy the emoji to global system clipboard
    QApplication.instance().clipboard().setText(text, QClipboard.Mode.Clipboard)
    assert QApplication.instance().clipboard().text(QClipboard.Mode.Clipboard) == text
    logger.info('Text copied to clipboard: %s', text)

    # And raise a desktop notification about it ...

    # Export emoji to icon for the notification
    qicon, icon_fname = None, None
    try:
        text_is_emoji = len(text) == 1
        if text_is_emoji:
            def _emoji_to_qicon(text, filename):
                pixmap = QPixmap(128, 128)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                from .tabs import EmojiTab
                font = QFont(EmojiTab.Delegate.ICON_FONT)
                font.setPixelSize(int(round(pixmap.rect().height() * .95)))
                painter.setFont(font)
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
                del painter  # https://stackoverflow.com/a/59605570/1090455
                res = pixmap.toImage().save(filename)
                if not res:
                    logger.warning('Failed to save emoji icon to "%s"', filename)
                return QIcon(pixmap)

            with NamedTemporaryFile(prefix=QApplication.instance().applicationName() + '-',
                                    suffix='.png', delete=False) as fd:
                qicon = _emoji_to_qicon(text, fd.name)
                icon_fname = fd.name

        notification_msg = [QApplication.instance().applicationName(),
                            f'Text {text!r} copied to clipboard.']
        if shutil.which('notify-send'):
            # XDG notification looks better than QSystemTrayIcon message, so try it first
            subprocess.run(['notify-send',
                            '--expire-time', '5000',
                            '--icon', icon_fname or 'info',
                            '--urgency', 'low',
                            *notification_msg])
        elif QSystemTrayIcon.isSystemTrayAvailable():
            from efck.gui import ICON_DIR

            tray = QSystemTrayIcon(QIcon(QPixmap(str(ICON_DIR / 'awesome-emoji.png'))),
                                   QApplication.instance(), visible=True)
            if qicon:
                notification_msg.append(qicon)  # FIXME: Why isn't qicon shown in the tooltip???
                # notification_msg.append(QSystemTrayIcon.Information)  # Yet this works
            tray.showMessage(*notification_msg, msecs=5000)
        else:
            logger.warning('No desktop notification system (notify-send) or systray detected')
    finally:
        if icon_fname:
            os.remove(icon_fname)


def _type_windos(text):
    import ctypes
    from ctypes.wintypes import DWORD, LONG, WORD, PULONG

    # God help us!

    # Adapted from:
    # https://github.com/Drov3r/Forza/blob/b3e489c1447f2fdc46081e053008aaa1ab77a12a/control.py#L63
    # https://stackoverflow.com/questions/22291282/using-sendinput-to-send-unicode-characters-beyond-uffff

    class KeyboardInput(ctypes.Structure):
        _fields_ = [("wVk", WORD),
                    ("wScan", WORD),
                    ("dwFlags", DWORD),
                    ("time", DWORD),
                    ("dwExtraInfo", PULONG)]

    class HardwareInput(ctypes.Structure):
        _fields_ = [("uMsg", DWORD),
                    ("wParamL", WORD),
                    ("wParamH", WORD)]

    class MouseInput(ctypes.Structure):
        _fields_ = [("dx", LONG),
                    ("dy", LONG),
                    ("mouseData", DWORD),
                    ("dwFlags", DWORD),
                    ("time", DWORD),
                    ("dwExtraInfo", PULONG)]

    class Input_I(ctypes.Union):
        _fields_ = [("ki", KeyboardInput),
                    ("mi", MouseInput),
                    ("hi", HardwareInput)]

    class Input(ctypes.Structure):
        _fields_ = [("type", DWORD),
                    ("ii", Input_I)]

    def as_wchars(ch):
        assert len(ch) == 1, (ch, len(ch))
        bytes = ch.encode('utf-16be')
        while bytes:
            yield int.from_bytes(bytes[:2], 'big')
            bytes = bytes[2:]

    TYPE_KEYBOARD_INPUT = 1
    KEYEVENTF_UNICODE = 0x4
    KEYEVENTF_KEYUP = 0x2
    KEYEVENTF_KEYDOWN = 0

    inputs = []
    for ch in text:
        for wch in as_wchars(ch):
            for flag in (KEYEVENTF_KEYDOWN,
                         KEYEVENTF_KEYUP):
                input = Input(TYPE_KEYBOARD_INPUT)
                # XXX: Assuming ctypes.Structure is memset to 0 at initialization?
                input.ii.ki.wScan = WORD(wch)
                input.ii.ki.dwFlags = KEYEVENTF_UNICODE | flag
                inputs.append(input)

    inputs = (Input * len(inputs))(*inputs)
    n = ctypes.windll.user32.SendInput(len(inputs), inputs, ctypes.sizeof(Input))
    assert n == len(inputs)
    return 0
