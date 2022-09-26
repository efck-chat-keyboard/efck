import copy
import logging

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
            for tab in self.nativeParentWidget().tabs:
                tab.init_delegate(zoom=zoom / 100)

        change_zoom_timer = QTimer(
            parent=self,
            singleShot=True,
            timeout=_change_zoom,
            interval=200)

        main_box = QGroupBox(self)
        self.layout().addWidget(main_box)
        main_box.setLayout(QVBoxLayout(main_box))
        force_clipboard_cb = QCheckBox(
            'Force &clipboard',
            parent=self,
            toolTip='Copy selected emoji/text into the clipboard in addition to typing it out. \n'
                    "Useful if typeout (default action) doesn't work on your system.")
        force_clipboard_cb.stateChanged.connect(
            lambda state: config_state.__setitem__('force_clipboard', bool(state)))
        main_box.layout().addWidget(force_clipboard_cb)

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

    def save_dirty(self) -> bool:
        """Returns True if config had changed and emoji need reloading"""
        from ..config import dump_config, config_state
        logger.debug('Saving config state if changed')
        if config_state != self._initial_config:
            dump_config()
            self._initial_config = copy.deepcopy(config_state)
            return True
