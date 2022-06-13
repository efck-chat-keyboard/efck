from __future__ import annotations

import logging
import string
from pathlib import Path

from .qt import *

logger = logging.getLogger(__name__)

ICON_DIR = Path(__file__).parent / 'icons'


def fire_after(self, timer_attr, callback, interval_ms):
    try:
        getattr(self, timer_attr).start()
    except AttributeError:
        timer = QTimer(self, singleShot=True, timeout=callback, interval=interval_ms)
        setattr(self, timer_attr, timer)
        timer.start()


class MainWindow(QTabWidget):
    def __init__(self):
        # GUI programming is realy messy, right?

        from .config import config_state

        def _initial_window_geometry():
            mouse_pos = QCursor.pos()
            geometry = config_state['window_geometry']
            logger.debug('Window geometry: %s', geometry)
            valid_geom = QGuiApplication.primaryScreen().availableGeometry()
            top_left = [max(mouse_pos.x() - geometry[0], valid_geom.x() + 20),
                        max(mouse_pos.y() - geometry[1], valid_geom.y() + 20)]
            return top_left + geometry

        # Init the main app/tabbed widget
        super().__init__(
            windowTitle=QApplication.instance().applicationName(),
            geometry=QRect(*_initial_window_geometry()),
        )
        self.setWindowFlags(Qt.WindowType.Dialog |
                            Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setCornerWidget(QLabel(" ef'ck ", margin=4), Qt.Corner.TopLeftCorner)

        # Populate tabs
        from .tab import Tab
        from . import tabs; tabs  # This makes all the Tabs available via Tab.__subclasses__
        from .tabs._options import OptionsTab

        # on-text-edited handler
        def on_text_edited():
            tab = self.tabs[self.currentIndex()]
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
            timeout=on_text_edited,
            interval=LineEdit.TIMEOUT_INTERVAL)

        options_tab = OptionsTab(parent=self)
        options_tab.destroyed.connect(lambda: options_tab.save_dirty())
        scroll_area = QScrollArea(self, widgetResizable=True)
        scroll_area.setWidget(options_tab)

        self.tabs: list[Tab] = []
        tab_classes = {i.__name__: i for i in Tab.__subclasses__()}.values()  # Avoid dupes due to imports
        tab_classes = sorted(tab_classes, key=lambda x: x.__name__)
        logger.info('Found tabs: %s', tab_classes)
        for tab_class in tab_classes:
            tab = tab_class(parent=self,
                            options_tab=options_tab,
                            textEdited=text_changed_timer.start,
                            activated=self.on_activated)
            self.addTab(tab, tab.icon, tab.label)
            self.tabs.append(tab)

        self.addTab(
            scroll_area,
            QIcon.fromTheme(
                'preferences-system',
                QIcon(QPixmap.fromImage(QImage(str(ICON_DIR / 'gears.png'))))),
            '&Options')

        OPTIONS_TAB_IDX = len(self.tabs)
        prev_idx = 0
        prev_text = ''

        # on-tab-changed logic
        def on_tab_changed(idx):
            nonlocal prev_idx, prev_text, options_tab
            logger.debug('New tab %d, prev %d', idx, prev_idx)
            config_state['selected_tab'] = idx

            # Carry over line edit text
            if prev_idx != OPTIONS_TAB_IDX:
                prev_text = self.tabs[prev_idx].line_edit.text()
            if idx != OPTIONS_TAB_IDX:
                tab = self.tabs[idx]
                if tab.line_edit.text() != prev_text:
                    tab.line_edit.setText(prev_text)
                    # TODO: Make sure this fires textEdited handler
                tab.line_edit.setFocus()

            if prev_idx == OPTIONS_TAB_IDX:
                # Reload models
                if options_tab.save_dirty():
                    for tab in self.tabs:
                        tab.reset_model()
            prev_idx = idx

        self.currentChanged.connect(on_tab_changed)

        # End in the following state and wait for user input
        on_text_edited()
        self.tabs[self.currentIndex()].line_edit.setFocus()
        options_tab.findChild(QSlider).setFocus()  # On Options tab, set focus to first child
        self.setCurrentIndex(config_state['selected_tab'])

    def resizeEvent(self, event: QResizeEvent):
        from .config import config_state, dump_config

        size = event.size()
        old_geometry = config_state['window_geometry'][-2:]
        new_geometry = [size.width(), size.height()]
        config_state['window_geometry'][-2:] = new_geometry
        # Save new window size in the config
        if old_geometry != new_geometry and not (self.isFullScreen() or self.isMaximized()):
            fire_after(self, 'timer_reload_config', dump_config, 1000)
        super().resizeEvent(event)

    @staticmethod
    def _is_alt_numeric_shortcut(event, *, _digits=tuple(string.digits[1:])):
        return event.text() in _digits and event.modifiers() & Qt.KeyboardModifier.AltModifier

    def keyPressEvent(self, event: QKeyEvent):
        event.accept()
        key = event.key()
        text = event.text()
        logger.debug('Keypress event: key=%x modifiers=%x text="%s"',
                     key,
                     getattr(event.modifiers(), 'value', event.modifiers()),  # PyQt6
                     text)
        # Escape key exits the app
        if key == Qt.Key.Key_Escape or event.matches(QKeySequence.StandardKey.Cancel):
            QApplication.instance().quit()

        tab_index = self.currentIndex()
        OPTIONS_TAB_IDX = len(self.tabs)
        if tab_index == OPTIONS_TAB_IDX:
            return

        tab = self.tabs[self.currentIndex()]
        view = tab.view

        # Alt+[1-9] selects and activates the corresponding view item
        if self._is_alt_numeric_shortcut(event):
            view.selectionModel().clearCurrentIndex()
            mi = view.model().index(int(text) - 1, 0)
            view.selectionModel().select(mi, QItemSelectionModel.SelectionFlag.ClearAndSelect)
            # HACK: HACK HACK. It types out nothing without some 20ms delay, wtf? Have tried:
            #     * view.keyPressEvent(synthetic_enter_event)
            #     * tab.line_edit.returnPressed.emit()
            #     * view.activated.emit(mi)
            #     * direct call to self.on_activated()
            QApplication.instance().processEvents()  # Not sure if this needed
            QTimer.singleShot(self.BUGGY_ALT_NUMERIC_KEYPRESS_SLEEP_MS, self.on_activated)
            return

        # Let the view handle the move event
        if key not in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            view.setFocus()  # Need temporary focus to handle the event
            view.keyPressEvent(event)
            tab.line_edit.setFocus()

    BUGGY_ALT_NUMERIC_KEYPRESS_SLEEP_MS = 100
    WM_SWITCH_ACTIVE_WINDOW_SLEEP_MS = 100

    def on_activated(self):
        """On listView activation, type out the characters and exit the app"""
        tab = self.tabs[self.currentIndex()]

        # Hide our app window before typing
        self.hide()
        # Give WM time to switch active window / focus
        QApplication.instance().processEvents()
        QThread.currentThread().msleep(self.WM_SWITCH_ACTIVE_WINDOW_SLEEP_MS)

        tab.activated()
        QApplication.instance().quit()


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
        line_edit.returnPressed.connect(activated)
        # line_edit.returnPressed.connect(activated, Qt.QueuedConnection)
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
        # view.activated.connect(activated, Qt.QueuedConnection)
        self.layout().addWidget(line_edit)
        self.layout().addWidget(view)

        self.model = self.Model(parent=self)
        self._model_was_init = False
        self.delegate = self.Delegate(parent=self)
        self.init_delegate(zoom=config_state.get('zoom', 100) / 100)
        view.setModel(self.model)
        view.setItemDelegate(self.delegate)

        config_part = config_state.get(self.__class__.__name__, {})  # TODO
        options_section: QGroupBox = self.Options(config=config_part, parent=None)
        if options_section.children():
            config_state[self.__class__.__name__] = config_part
            options_section.setParent(self)
            options_tab.add_section(options_section)

    def init_delegate(self, **kwargs):
        """Call this whenever options change that would influence rendering by the delegate"""
        if hasattr(self.delegate, 'init'):
            self.delegate.init(**kwargs)

    def showEvent(self, ev):
        # Lazy init the model on first show
        if not self._model_was_init:
            self.reset_model()
        self._model_was_init = True

    def reset_model(self):
        self.model.beginResetModel()
        self.model.init()
        self.model.endResetModel()
        # Apply text filter and preselect
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
        logger.debug('Line edit Keypress: key=%x modifiers=%x text="%s"',
                     event.key(),
                     getattr(event.modifiers(), 'value', event.modifiers()),  # PyQt6
                     event.text())
        # Ignore Alt+[0-9] (numbered item activation)
        if MainWindow._is_alt_numeric_shortcut(event):
            return event.ignore()
        # Ignore e.g. Ctrl+Arrow keys to skip words
        if event.key() in self.ignore_keys and not event.modifiers():
            return event.ignore()
        return super().keyPressEvent(event)
