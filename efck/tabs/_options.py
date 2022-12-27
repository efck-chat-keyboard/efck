import copy
import logging

import pynput.keyboard

from ..qt import *


logger = logging.getLogger(__name__)


class OptionsTab(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.setLayout(QVBoxLayout(self))

        from ..config import config_state

        self._initial_config = copy.deepcopy(config_state)

        def zoom_changed(value):
            nonlocal ONE_TICK_IN_PCT, slider_label, change_zoom_timer
            slider_label.setText(f'Zoom: {value * ONE_TICK_IN_PCT:3d}%')
            change_zoom_timer.start()

        def _change_zoom():
            nonlocal ONE_TICK_IN_PCT, config_state, zoom_slider, self
            config_state['zoom'] = zoom = zoom_slider.value() * ONE_TICK_IN_PCT
            logger.info('Set zoom: %f', zoom)

        change_zoom_timer = QTimer(
            parent=self,
            singleShot=True,
            timeout=_change_zoom,
            interval=200)

        main_box = QGroupBox(self)
        self.layout().addWidget(main_box)
        main_box.setLayout(QVBoxLayout(main_box))

        check = QCheckBox(
            'Force &clipboard',
            parent=self,
            checked=config_state['force_clipboard'],
            toolTip='Copy selected emoji/text into the clipboard in addition to typing it out. \n'
                    "Useful if typeout (default action) doesn't work on your system.")
        check.stateChanged.connect(
            lambda state: config_state.__setitem__('force_clipboard', bool(state)))
        main_box.layout().addWidget(check)

        check = QCheckBox(
            'Fast startup (background service) with keyboard hotkey:',
            parent=self,
            checked=config_state['tray_agent'],
            toolTip='Minimize app to background instead of closing it. '
                    'This enables much faster subsequent startup.')
        check.stateChanged.connect(
            lambda state: (config_state.__setitem__('tray_agent', bool(state)),
                           hotkey_edit.setEnabled(state)))

        url = 'https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key'
        hotkey_edit = QLineEdit(
            config_state['hotkey'],
            parent=self,
            enabled=check.isChecked(),
            toolTip=f'Hotkey syntax format is as accepted by '
                    f'<b><code>pynput.keyboard.HotKey</code></b>: <a href="{url}">{url}</a>'
        )
        hotkey_edit.textEdited.connect(
            lambda text: is_hotkey_valid(text) and config_state.__setitem__('hotkey', text))

        def is_hotkey_valid(text):
            try:
                pynput.keyboard.HotKey.parse(text)
            except ValueError:
                hotkey_edit.setStyleSheet('QLineEdit {border: 3px solid red}')
                return False
            hotkey_edit.setStyleSheet('')
            return True

        box = QWidget()
        box.setLayout(QHBoxLayout())
        box.layout().setContentsMargins(0, 0, 0, 0)
        box.layout().addWidget(check)
        box.layout().addWidget(hotkey_edit)
        main_box.layout().addWidget(box)

        box = QWidget(self)
        main_box.layout().addWidget(box)
        box.setLayout(QHBoxLayout(box))
        box.layout().setContentsMargins(0, 0, 0, 0)
        ONE_TICK_IN_PCT = 5
        zoom_slider = QSlider(
            parent=self,
            orientation=Qt.Orientation.Horizontal,
            tickPosition=QSlider.TickPosition.TicksBothSides,
            minimum=70 // ONE_TICK_IN_PCT,
            maximum=200 // ONE_TICK_IN_PCT,
            pageStep=30 // ONE_TICK_IN_PCT,
            singleStep=10 // ONE_TICK_IN_PCT,
            tickInterval=10 // ONE_TICK_IN_PCT,
            value=config_state['zoom'] // ONE_TICK_IN_PCT,
        )
        zoom_slider.valueChanged.connect(zoom_changed)
        slider_label = QLabel(f'Z&oom: {zoom_slider.value() * ONE_TICK_IN_PCT:3d}%')
        slider_label.setBuddy(zoom_slider)
        box.layout().addWidget(slider_label)
        box.layout().addWidget(zoom_slider)

    def add_section(self, name, widget: QWidget):
        box = QGroupBox(name.replace('&', ''), self)
        widget.setParent(box)
        box.setLayout(QVBoxLayout(box))
        box.layout().setContentsMargins(0, 0, 0, 0)
        box.layout().addWidget(widget)
        self.layout().addWidget(box)

    def hideEvent(self, event):
        if self.save_dirty():
            # Reload models
            for tab in self.nativeParentWidget().tabs:
                tab.reset_model()

    def save_dirty(self, exiting=False) -> bool:
        """Returns True if config had changed and emoji need reloading"""
        from ..config import dump_config, config_state
        logger.debug('Saving config state if changed')
        if config_state != self._initial_config:
            dump_config()
            self._initial_config = copy.deepcopy(config_state)

            if not exiting:
                self.nativeParentWidget().reset_hotkey_listener()

                for tab in self.nativeParentWidget().tabs:
                    tab.init_delegate(config=config_state.get(tab.__class__.__name__),
                                      zoom=config_state.get('zoom', 100) / 100)
            return True
