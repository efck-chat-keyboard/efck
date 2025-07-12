import atexit
import logging
import os
import signal
from pathlib import Path

from . import IS_MACOS, IS_WIDOWS
from .qt import *

logger = logging.getLogger(__name__)

ICON_DIR = Path(__file__).parent / 'icons'

NUMERIC_KEYS = {Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3,
                Qt.Key.Key_4, Qt.Key.Key_5, Qt.Key.Key_6,
                Qt.Key.Key_7, Qt.Key.Key_8, Qt.Key.Key_9}

OUR_SIGUSR1 = signal.SIGBREAK if IS_WIDOWS else signal.SIGUSR1


def fire_after(self, timer_attr, callback, interval_ms):
    try:
        getattr(self, timer_attr).start()
    except AttributeError:
        timer = QTimer(self, singleShot=True, timeout=callback, interval=interval_ms)
        setattr(self, timer_attr, timer)
        timer.start()


class _HasSizeGripMixin:
    SIZEGRIP_SIZE = 16

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grip = self._grip = QSizeGrip(self)
        grip.resize(self.SIZEGRIP_SIZE, self.SIZEGRIP_SIZE)
        self.__reposition()

    def __reposition(self):
        self._grip.move(self.rect().right() - self.SIZEGRIP_SIZE,
                        self.rect().bottom() - self.SIZEGRIP_SIZE)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.__reposition()


class _WindowMovableMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._click_point = None

    def mousePressEvent(self, event: QMouseEvent):
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self._click_point = event_position(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._click_point:
            if self.windowHandle().startSystemMove():
                self.mouseReleaseEvent(event)
            else:
                self.move(self.mapToGlobal(event_position(event) - self._click_point))

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._click_point = None


class _AutoQuitOnFocusLostMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quit_timer = QTimer(
            self, interval=1500, singleShot=True,
            timeout=lambda: (
                QApplication.quit()
                if len(self.current_tab.line_edit.text()) < 10 else
                None))
        QApplication.instance().applicationStateChanged.connect(self.on_app_state_changed)

    def on_app_state_changed(self, state):
        if state == Qt.ApplicationState.ApplicationInactive:
            self.quit_timer.start()
        elif state == Qt.ApplicationState.ApplicationActive:
            self.quit_timer.stop()


class MainWindow(_HasSizeGripMixin,
                 _WindowMovableMixin,
                 _AutoQuitOnFocusLostMixin,
                 QTabWidget):
    def __init__(self):
        # GUI programming is realy messy, right?

        from .config import config_state

        # Init the main app/tabbed widget
        super().__init__(
            windowTitle=QApplication.instance().applicationName(),
            windowIcon=QIcon(str(ICON_DIR / 'logo.png')),
            documentMode=True,
            usesScrollButtons=True,
            # FIXME: Reduce tabs right margin on macOS
            #  https://forum.qt.io/topic/119371/text-in-qtabbar-on-macos-is-truncated-or-elided-by-default-although-there-is-empty-space/10
        )
        self.reset_window_position()
        self.install_sigusr1_handler()
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        # Minimize padding on macOS
        self.setAttribute(Qt.WidgetAttribute.WA_MacMiniSize)
        self.tabBar().setAttribute(Qt.WidgetAttribute.WA_MacNormalSize)  # But make sure tabs labels expand

        # Setup corner widget

        from . import __website__

        class CornerWidget(QWidget):
            def __init__(self, parent):
                super().__init__(parent, toolTip=f'Emoji filter / Unicode chat keyboard\n\n{__website__}')
                self.setLayout(QVBoxLayout(self))
                self.layout().setContentsMargins(8, 4, 15, 4)

                class Label(QLabel):
                    def __init__(self, parent):
                        palette: QPalette = QApplication.instance().palette()
                        palette.setColor(QPalette.ColorRole.Link,
                                         palette.color(QPalette.ColorRole.WindowText))
                        QApplication.instance().setPalette(palette)
                        super().__init__(
                            f'<a href="{__website__}"><b>EF*CK</b></a>',
                            textFormat=Qt.TextFormat.RichText,
                            textInteractionFlags=(Qt.TextInteractionFlag.LinksAccessibleByMouse |
                                                  Qt.TextInteractionFlag.LinksAccessibleByKeyboard),
                            openExternalLinks=True,
                            parent=parent,
                        )

                self.layout().addWidget(Label(self))

        corner_widget = CornerWidget(self)
        self.setCornerWidget(corner_widget, Qt.Corner.TopLeftCorner)

        close_button = QPushButton(
            icon=self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton),
            flat=True,
            toolTip='Close',
            parent=self,
        )
        close_button.clicked.connect(QApplication.instance().quit)
        self.setCornerWidget(close_button, Qt.Corner.TopRightCorner)

        # Populate tabs

        from .tab import Tab
        from . import tabs; tabs  # This makes all the Tabs available via Tab.__subclasses__  # noqa: E702
        from .tabs._options import OptionsTab

        def _on_text_edited():
            tab = self.current_tab
            text = tab.line_edit.text()
            logger.debug('Text edited: %s', text)
            if hasattr(tab.model, 'set_text'):
                tab.model.set_text(text)
            if hasattr(tab.delegate, 'set_text'):
                tab.delegate.set_text(text)
            tab._reset_view_select_top_item()

        text_changed_timer = QTimer(
            parent=self,
            singleShot=True,
            timeout=_on_text_edited,
            interval=LineEdit.TIMEOUT_INTERVAL)

        options_tab = OptionsTab(parent=self)
        atexit.register(options_tab.save_dirty, exiting=True)
        scroll_area = QScrollArea(self, widgetResizable=True, frameShape=QScrollArea.Shape.NoFrame)
        scroll_area.setWidget(options_tab)

        qt_set_sequence_auto_mnemonic(True)  # Enable tab mnemonics (or at least shortcuts) on macOS

        self.tabs: list[Tab] = []
        tab_classes = {i.__name__: i for i in Tab.__subclasses__()}.values()  # Avoid dupes due to imports
        tab_classes = sorted(tab_classes, key=lambda x: x.__name__)
        logger.info('Found tabs: %s', tab_classes)
        for tab_class in tab_classes:
            tab = tab_class(
                parent=self,
                options_tab=options_tab,
                textEdited=text_changed_timer.start,
                activated=self.on_activated,
            )
            self.addTab(tab, tab.icon, tab.label)
            self.tabs.append(tab)
        assert self.tabs, 'No tab classes found. Are efck.tabs.* modules present?'

        self.addTab(
            scroll_area,
            QIcon.fromTheme(
                'preferences-system',
                QIcon(QPixmap.fromImage(QImage(str(ICON_DIR / 'gears.png'))))),
            '&Options')

        OPTIONS_TAB_IDX = len(self.tabs)
        prev_idx = 0
        prev_text = ''

        def _on_tab_changed(idx):
            nonlocal prev_idx, prev_text, options_tab
            logger.debug('Curr tab %d, prev %d', idx, prev_idx)
            config_state['selected_tab'] = idx

            # Carry over line edit text
            if prev_idx != OPTIONS_TAB_IDX:
                prev_text = self.tabs[prev_idx].line_edit.text()
            if idx != OPTIONS_TAB_IDX:
                tab = self.tabs[idx]
                if tab.line_edit.text() != prev_text:
                    tab.line_edit.setText(prev_text)
                tab.line_edit.setFocus()

            prev_idx = idx

        self.currentChanged.connect(_on_tab_changed)

        # End in the following state and wait for user input

        self.current_tab.line_edit.setFocus()
        options_tab.findChild(QSlider).setFocus()  # On Options tab, set focus to first child
        self.setCurrentIndex(config_state['selected_tab'])
        self.raise_()
        self.activateWindow()

    def resizeEvent(self, event: QResizeEvent):
        from .config import config_state, dump_config

        size = event.size()
        old_geometry = config_state['window_geometry'][-2:]
        new_geometry = [size.width(), size.height()]
        config_state['window_geometry'][-2:] = new_geometry
        # Save new window size in the config on disk
        if old_geometry != new_geometry and not (self.isFullScreen() or self.isMaximized()):
            fire_after(self, 'timer_reload_config', dump_config, 1000)
        super().resizeEvent(event)

    @staticmethod
    def _is_alt_numeric_shortcut(event):
        return event.modifiers() & Qt.KeyboardModifier.AltModifier and event.key() in NUMERIC_KEYS

    def keyPressEvent(self, event: QKeyEvent):
        event.accept()
        key = event.key()
        text = event.text().strip()
        logger.debug('TabWidget keypress: key=%s modifiers=%x text="%s"',
                     key,
                     getattr(event.modifiers(), 'value', event.modifiers()),  # PyQt6
                     text)
        # Escape key exits the app / minimizes to tray
        if key == Qt.Key.Key_Escape or event.matches(QKeySequence.StandardKey.Cancel):
            self.exit()

        tab = self.current_tab
        # Don't handle other keypresses on Options tab here
        if not tab:
            return
        view = tab.view

        # Alt+[1-9] selects and activates the corresponding view item
        if self._is_alt_numeric_shortcut(event):
            view.selectionModel().clearCurrentIndex()
            num = key - Qt.Key.Key_0
            mi = view.model().index(num - 1, 0)
            if mi.isValid():
                view.selectionModel().setCurrentIndex(mi, QItemSelectionModel.SelectionFlag.ClearAndSelect)
                QTimer.singleShot(self.BUGGY_ALT_NUMERIC_KEYPRESS_SLEEP_MS, self.on_activated)
            return

        if key in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            return QTimer.singleShot(10, self.on_activated)
        elif key in (Qt.Key.Key_Control,
                     Qt.Key.Key_Shift,
                     Qt.Key.Key_Meta,
                     Qt.Key.Key_AltGr,
                     Qt.Key.Key_Alt):
            # Skip modifier keys when pressed alone since maybe a
            # valid line edit action follows
            pass
        else:
            # Let the view handle the move event
            view.setFocus()  # Need temporary focus to handle the event
            view.keyPressEvent(event)
            tab.line_edit.setFocus()

    BUGGY_ALT_NUMERIC_KEYPRESS_SLEEP_MS = 100
    WM_SWITCH_ACTIVE_WINDOW_SLEEP_MS = 100
    if IS_MACOS:
        # On macOS, delays is not needed since we have 'sleep .2'
        # in the typeout script
        BUGGY_ALT_NUMERIC_KEYPRESS_SLEEP_MS = 1
        WM_SWITCH_ACTIVE_WINDOW_SLEEP_MS = 1

    @property
    def current_tab(self):
        try:
            return self.tabs[self.currentIndex()]
        except IndexError:
            return None  # I.e. on Options tab

    def on_activated(self):
        """On listView activation, type out the characters and exit the app"""
        tab = self.current_tab

        # Ensure some view item is selected
        mi = tab.view.currentIndex()
        if not mi.isValid():
            return

        logger.info('Activated item %d', mi.row())

        from .config import config_state

        force_clipboard = config_state['force_clipboard']

        if tab.activation_can_fail:
            # Tab will tell us if success (such as a DND op)
            failure = tab.activated(force_clipboard=force_clipboard)
            if failure:
                logger.debug("%s.activated() failed: %s", tab.__class__.__name__, failure)
                return  # without app exit
        else:
            # Hide our app window before typing
            self.close()
            # Give WM time to switch active window / focus
            QApplication.instance().processEvents()
            QThread.currentThread().msleep(self.WM_SWITCH_ACTIVE_WINDOW_SLEEP_MS)
            QApplication.instance().processEvents()

            tab.activated(force_clipboard=force_clipboard)

        self.exit()

    def exit(self):
        from .config import config_state

        if config_state['tray_agent']:
            super().close()
            if self.current_tab:
                self.current_tab.line_edit.clear()
        else:
            QApplication.instance().quit()

    _listener = None

    def reset_hotkey_listener(self):
        import pynput.keyboard

        from .config import config_state

        if self._listener:
            self._listener.stop()

        def on_hotkey():
            logger.info(f'Hotkey "{config_state["hotkey"]}" pressed. Raising window.')
            nonlocal self
            self.reset_window_position()
            self.show()
            self.raise_()
            return True

        if config_state['tray_agent']:
            try:
                self._listener = pynput.keyboard.GlobalHotKeys({config_state['hotkey']: on_hotkey})
                self._listener.start()
            except ValueError:
                logger.exception('Invalid hotkey??? %s', config_state)

    def reset_window_position(self):
        from .config import config_state

        mouse_pos = QCursor.pos() + QPoint(0, -40)  # distance from mouse padding
        geometry = config_state['window_geometry']
        logger.debug('Window geometry: %s', geometry)
        valid_geom = QGuiApplication.primaryScreen().availableGeometry()
        PAD_PX = 50
        top_left = [max(mouse_pos.x() - geometry[0], valid_geom.x() + PAD_PX),
                    max(mouse_pos.y() - geometry[1], valid_geom.y() + PAD_PX)]
        geometry = [min(geometry[0], valid_geom.width() - 2 * PAD_PX),
                    min(geometry[1], valid_geom.height() - 2 * PAD_PX)]
        self.setGeometry(QRect(*top_left + geometry))

    def install_sigusr1_handler(self):
        r_fd, w_fd = os.pipe()
        if not IS_WIDOWS:
            os.set_blocking(w_fd, False)
        atexit.register(os.close, r_fd)
        atexit.register(os.close, w_fd)
        self._notifier = notifier = QSocketNotifier(r_fd, QSocketNotifier.Type.Read, self)
        # https://stackoverflow.com/questions/4938723/what-is-the-correct-way-to/37229299#37229299
        signal.set_wakeup_fd(w_fd)
        signal.signal(OUR_SIGUSR1, lambda sig, frame: None)

        def sigusr1_received():
            nonlocal notifier, self, r_fd
            notifier.setEnabled(False)
            signum = ord(os.read(r_fd, 1))
            if signum == OUR_SIGUSR1:
                logger.info('Handled SIGUSR1. Showing up!')
                self.reset_window_position()
                self.show()
                self.raise_()
            notifier.setEnabled(True)

        notifier.activated.connect(sigusr1_received)


class _TabPrivate(QWidget):
    def __init__(self, parent, options_tab, textEdited, activated):
        from .config import config_state

        super().__init__(parent=parent)
        self.setLayout(QVBoxLayout(self))

        # Add line edit and list view widgets
        default_line_edit_kwargs = dict(
            parent=self,
        )
        self.line_edit = line_edit = LineEdit(
            ignore_keys=self.line_edit_ignore_keys,
            **default_line_edit_kwargs | self.line_edit_kwargs,
        )
        line_edit.textEdited.connect(textEdited)
        line_edit.setAttribute(Qt.WidgetAttribute.WA_MacNormalSize)  # Override main widget's MacMiniSize

        default_list_view_kwargs = dict(
            parent=self,
            flow=QListView.Flow.TopToBottom,
            resizeMode=QListView.ResizeMode.Adjust,
            layoutMode=QListView.LayoutMode.Batched,
            selectionMode=QListView.SelectionMode.SingleSelection,
            horizontalScrollBarPolicy=Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
            verticalScrollMode=QListView.ScrollMode.ScrollPerPixel,
            uniformItemSizes=True,
            textElideMode=Qt.TextElideMode.ElideRight,
        )
        self.view = view = self.View(
            **default_list_view_kwargs | self.list_view_kwargs
        )
        view.activated.connect(activated)
        self.layout().addWidget(line_edit)
        self.layout().addWidget(view)

        self.model = self.Model(parent=self)
        self._model_was_init = False
        self.delegate = self.Delegate(parent=self)
        config_part = config_state.get(self.__class__.__name__, {})
        self.init_delegate(config=config_part, zoom=config_state.get('zoom', 100) / 100)
        view.setModel(self.model)
        view.setItemDelegate(self.delegate)

        options_section: QGroupBox = self.Options(config=config_part, parent=None)
        if options_section.children():
            config_state[self.__class__.__name__] = config_part
            options_section.setParent(self)
            options_tab.add_section(self.label, options_section)

    def init_delegate(self, **kwargs):
        """Call this whenever options change that would influence rendering by the delegate"""
        if hasattr(self.delegate, 'init'):
            self.delegate.init(**kwargs)

    def showEvent(self, ev):
        # Lazy init the model on first show
        was_init = self._model_was_init
        self._model_was_init = True
        if not was_init:
            self.reset_model()

    def reset_model(self):
        if self._model_was_init:
            from .config import config_state

            config_part = config_state.get(self.__class__.__name__, {})
            self.model.beginResetModel()
            self.model.init(config=config_part)
            self.model.endResetModel()
            self._reset_view_select_top_item()
            self.line_edit.textEdited.emit(self.line_edit.text())

    def _reset_view_select_top_item(self):
        view: QListView = self.view
        prev_current_index = view.selectionModel().currentIndex()
        view.reset()
        current_index = (view.model().index(0, 0)
                         if self.line_edit_resets_selection or not prev_current_index.isValid() else
                         prev_current_index)
        view.selectionModel().setCurrentIndex(
            current_index, QItemSelectionModel.SelectionFlag.ClearAndSelect)


class LineEdit(QLineEdit):
    TIMEOUT_INTERVAL = 130

    def __init__(self, *args, ignore_keys, **kwargs):
        super().__init__(*args, **kwargs)
        self.ignore_keys = ignore_keys

    def keyPressEvent(self, event: QKeyEvent):
        # Ignore Alt+[0-9] (numbered item activation)
        if MainWindow._is_alt_numeric_shortcut(event):
            return event.ignore()

        # Arrow keys on macOS set KeypadModifier
        modifiers = event.modifiers() & ~Qt.KeyboardModifier.KeypadModifier
        # Ignore e.g. Ctrl+Arrow keys to skip words
        if event.key() in self.ignore_keys and not modifiers:
            return event.ignore()

        logger.debug('LineEdit keypress: key=%s modifiers=%x text="%s"',
                     event.key(),
                     getattr(event.modifiers(), 'value', event.modifiers()),  # PyQt6
                     event.text().strip())
        return super().keyPressEvent(event)
