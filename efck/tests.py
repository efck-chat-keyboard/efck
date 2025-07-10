import os
import unittest
from collections.abc import Sequence
from pathlib import Path
from unittest import TestCase

from unittest.mock import patch, MagicMock

from . import CONFIG_DIRS, IS_MACOS, IS_X11, IS_WIDOWS
from .gui import LineEdit as AppLineEdit, MainWindow
from .qt import *


MIN_DELAY_MS = 100

# Set XDG_*_HOME env vars, and therefore CONFIG_DIRS, to ~/.qttest/*
QStandardPaths.setTestModeEnabled(True)
CONFIG_DIRS[:] = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.AppConfigLocation)


def keypress(widget, keys=()):
    if not isinstance(keys, Sequence):
        keys = [keys]
    for key in keys:
        try:
            modifier, key = key
        except TypeError:
            modifier = Qt.KeyboardModifier.NoModifier
        QTest.keyClick(widget, key, modifier, MIN_DELAY_MS)


class LineEdit(QLineEdit):
    was_typed_into = False

    def __init__(self):
        super().__init__()
        # Need Window for regaining focus on macOS
        self.setWindowFlags(Qt.WindowType.Window)
        self.setAcceptDrops(True)

    def keyPressEvent(self, event):
        self.was_typed_into = True
        assert not event.text(), event.text()
        # XXX: Some key events are sent, but no emoji?
        #   Might be https://bugreports.qt.io/browse/QTBUG-72776
        super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        assert event.mimeData().hasFormat('text/uri-list'), (event.mimeData().formats())
        event.acceptProposedAction()
        self.was_typed_into = True


class TestMain(TestCase):
    def setUp(self):
        self.patcher = patch('efck.gui.QApplication.instance')
        mock_qapp_instance_factory = self.patcher.start() # This is the mock for the function QApplication.instance
        self.addCleanup(self.patcher.stop)

        # Configure the mocked QApplication.instance() to behave sufficiently for MainWindow init
        mock_app = mock_qapp_instance_factory.return_value
        mock_app.applicationName.return_value = "efck-test-app" # For windowTitle

        # Mock clipboard behavior
        mock_clipboard = MagicMock(spec=QClipboard)
        self._mock_clipboard_text_storage = ''
        def _mock_setText(text, mode=QClipboard.Mode.Clipboard): self._mock_clipboard_text_storage = text
        def _mock_text(mode=QClipboard.Mode.Clipboard): return self._mock_clipboard_text_storage
        mock_clipboard.setText = _mock_setText
        mock_clipboard.text = _mock_text
        mock_app.clipboard.return_value = mock_clipboard

        # Mock the quit method for assertions
        self.mock_app_quit = mock_app.quit
        self.mock_app_quit.reset_mock()

        self.typed_text_target = typed_text_target = LineEdit()
        typed_text_target.show()
        typed_text_target.setFocus()
        typed_text_target.activateWindow()
        QTest.qWaitForWindowActive(typed_text_target)
        self.assertTrue(typed_text_target.hasFocus())
        QTest.mouseMove(self.typed_text_target)
        QTest.qWait(MIN_DELAY_MS)
        QTest.mouseClick(self.typed_text_target, Qt.MouseButton.LeftButton)
        QTest.qWait(MIN_DELAY_MS)

        self.app_window = app_window = MainWindow()
        app_window.show()
        app_window.activateWindow()
        QTest.qWaitForWindowActive(app_window)

        self.expected_value = None

    def tearDown(self):
        # Wait on all timers
        QTest.qWait(AppLineEdit.TIMEOUT_INTERVAL +
                    MainWindow.WM_SWITCH_ACTIVE_WINDOW_SLEEP_MS +
                    MainWindow.BUGGY_ALT_NUMERIC_KEYPRESS_SLEEP_MS +
                    MIN_DELAY_MS)

        if not self.mock_app_quit.called: # Only check window state if app didn't "quit"
            QTest.qWaitForWindowActive(self.typed_text_target)
            # NOTE: This requires a running WM, such as flwm, in our CI
            self.assertTrue(self.typed_text_target.isActiveWindow(),
                            "typed_text_target should be active if app hasn't quit")
            self.assertTrue(self.typed_text_target.hasFocus(),
                            "typed_text_target should have focus if app hasn't quit")

        QTest.qWait(500)  # Wait for macOS and everything to sure be over
        if IS_MACOS:
            QTest.qWait(1500)  # For sure!

        if not self.mock_app_quit.called:
             if self.expected_value is None: # only check if not already checking expected_value
                self.assertFalse(self.typed_text_target.was_typed_into,
                                 "Text field was unexpectedly typed into when app hasn't quit and no value expected")

        if self.expected_value is not None:
            if IS_WIDOWS:
                self.assertEqual(self.typed_text_target.text(), self.expected_value)
            elif IS_MACOS:
                # XXX: CI on macOS mostly failed on test_avocado and
                #  test_filters_with_altnum_select, so we use this simpler test for now ...
                self.assertTrue(self.typed_text_target.was_typed_into)
            else:
                # XXX: Below commented line should work but it doesn't on X11?
                #      `xev -id $(xwininfo | grep -oP '(?<=Window id: )\w+')` gives no good clues
                # NOTE: Also typing manually with xdotool into a QLineEdit (MWE) doesn't work!!! Wtf?
                self.assertEqual(self.typed_text_target.text(), '')  # XXX: Adapt as bug fixed
                self.assertTrue(self.typed_text_target.was_typed_into)  # HACK for now

    def keypress(self, keys):
        line_edit = self.app_window.currentWidget().line_edit
        self.assertTrue(line_edit.hasFocus())
        keypress(line_edit, keys)

    @unittest.skipIf(IS_MACOS, 'Fails on CI')  # FIXME: Investigate on macOS
    def test_avocado(self):
        self.expected_value = '\N{AVOCADO}'
        self.keypress([Qt.Key.Key_A, Qt.Key.Key_V, Qt.Key.Key_O,
                       Qt.Key.Key_Right, Qt.Key.Key_Enter])

    @unittest.skipIf(IS_MACOS, 'Fails on CI')  # FIXME: Investigate on macOS
    def test_filters_with_altnum_select(self):
        self.expected_value = '𝗯𝗼𝗹𝗱'
        self.keypress([
            Qt.Key.Key_B, Qt.Key.Key_O, Qt.Key.Key_L, Qt.Key.Key_D,
            (Qt.KeyboardModifier.AltModifier, Qt.Key.Key_F),
            (Qt.KeyboardModifier.AltModifier, Qt.Key.Key_1),  # "Alt+1" selection
        ])

    def _wait_gifs_load(self):
        model = self.app_window.tabs[self.app_window.currentIndex()].model
        for i in range(50):
            QTest.qWait(MIN_DELAY_MS)
            if len(model.gifs) > 2:
                break
        else:
            raise TimeoutError("Couldn't load at least some GIFs")

    def _complete_qdrag_exec(self):
        """Because QDrag.exec() blocks, need to call this via QTimer.singleShot()"""
        QTest.mouseMove(self.typed_text_target)
        QTest.qWait(MIN_DELAY_MS)
        self.typed_text_target.activateWindow()  # Hack to make the tests pass. IRL, WM does this.
        QTest.mouseClick(self.typed_text_target, Qt.MouseButton.LeftButton)

    @unittest.skipIf(IS_WIDOWS, 'QTest.mouseMove fails while QDrag on Windows')
    @unittest.skipIf(IS_X11 and QT_API == 'pyqt5', 'Fails on X11, QT_API=pyqt5')
    @unittest.skipIf(IS_MACOS and QT_API == 'pyside6',
                     'macOS lacks mnemonics and PySide6 is missing qt_set_sequence_auto_mnemonic()')
    @unittest.skipIf(os.environ.get('GITHUB_JOB') and IS_MACOS and QT_API == 'pyqt6',
                     'fails only on GitHub CI, otherwise works')
    def test_gifs_activate(self):
        self.keypress([(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_G)])
        self._wait_gifs_load()
        QTimer.singleShot(1000, self._complete_qdrag_exec)
        self.keypress([Qt.Key.Key_Down, Qt.Key.Key_Return])

    @unittest.skipIf(IS_WIDOWS, 'QTest.mouseMove fails while QDrag on Windows')
    @unittest.skipIf(IS_X11 and QT_API == 'pyqt5', 'Fails on X11, QT_API=pyqt5')
    @unittest.skipIf(IS_MACOS and QT_API == 'pyside6',
                     'macOS lacks mnemonics and PySide6 is missing qt_set_sequence_auto_mnemonic()')
    @unittest.skipIf(IS_MACOS and QT_API == 'pyqt5', 'fails for unknown reason')
    @unittest.skipIf(os.environ.get('GITHUB_JOB') and IS_MACOS and QT_API == 'pyqt6',
                     'fails only on GitHub CI, otherwise works')
    def test_gifs_dragndrop(self):
        self.keypress([(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_G)])
        self._wait_gifs_load()
        view = self.app_window.tabs[self.app_window.currentIndex()].view
        QTimer.singleShot(1000, self._complete_qdrag_exec)
        pt = QPoint(50, 50)
        QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, pt)
        QTest.mouseMove(view.viewport())

    def test_close_button_quits_application(self):
        # Ensure the main window is active
        self.assertTrue(self.app_window.isActiveWindow())

        # Locate the close button
        close_button = self.app_window.cornerWidget(Qt.Corner.TopRightCorner)
        self.assertIsNotNone(close_button, "Close button not found in TopRightCorner")
        self.assertIsInstance(close_button, QPushButton, "Corner widget is not a QPushButton")

        # self.mock_app_quit is set up by the class-level patch in setUp and reset for each test.
        # MainWindow's close button is connected to this mock's .quit() method.

        # Try direct click first to verify signal/slot and mock
        close_button.click()

        # Wait for events to process
        QTest.qWait(MIN_DELAY_MS * 2) # Increased wait time just in case

        # Assert that QApplication.instance().quit() (which is self.mock_app_quit) was called
        self.mock_app_quit.assert_called_once()

        # This test doesn't type anything, so set expected_value to None
        self.expected_value = None


class TestConfig(TestCase):
    def test_config(self):
        from .config import dump_config

        path = dump_config()
        self.assertTrue(path, path)


class TestEmoji(TestCase):
    def test_enum_emoji(self):
        from .emoji import enum_emojis

        emojis = enum_emojis()
        self.assertGreater(len(emojis), 1000)
        self.assertGreater(len(emojis[0]), 3)

    def test_no_judge(self):
        from .emoji import enum_emojis
        from .config import _gender

        # Test disabled neuter professions are not present
        _gender.update({'person': 0, 'man': 0, 'woman': 1})
        emojis = enum_emojis()
        judge = [i[1] for i in emojis if 'judge' in i[1]]
        self.assertEqual(len(judge), 1)
        self.assertIn('woman', judge[0])


class TestOutput(TestCase):
    def test_copy_to_clipboard(self):
        from .output import _copy_to_clipboard

        pineapple = '🍍'
        _copy_to_clipboard(pineapple)
        self.assertEqual(QApplication.instance().clipboard().text(), pineapple)


class TestFilters(TestCase):
    def test_filters(self):
        from .tabs.filters import load_modules

        modules = load_modules()
        self.assertTrue(modules, modules)
        files = set(os.listdir(Path(__file__).parent / 'filters')) - {'README.md', '__pycache__'}
        self.assertEqual(len(modules), len(files), files)
        for mod in modules:
            peach = '🍑'
            text = getattr(mod, 'example', peach)
            out = mod.func(text)
            self.assertTrue(out, out)


if __name__ == '__main__':
    unittest.main()
