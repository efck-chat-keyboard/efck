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
            nonlocal ONE_TICK_IN_PCT
            slider_label.setText(f'{value * ONE_TICK_IN_PCT}%')
            change_zoom_timer.start()

        def _change_zoom():
            nonlocal ONE_TICK_IN_PCT
            config_state['zoom'] = zoom = zoom_slider.value() * ONE_TICK_IN_PCT
            logger.info('Set zoom: %f', zoom)
            for tab in self.nativeParentWidget().tabs:
                tab.init_delegate(zoom=zoom / 100)

        change_zoom_timer = QTimer(
            parent=self,
            singleShot=True,
            timeout=_change_zoom,
            interval=200)

        box = QGroupBox('&Zoom Emoji')
        self.layout().addWidget(box)
        box.setLayout(QHBoxLayout(box))
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
        slider_label = QLabel(f'{zoom_slider.value() * ONE_TICK_IN_PCT}%')
        box.layout().addWidget(slider_label)
        box.layout().addWidget(zoom_slider)

    def add_section(self, box: QWidget):
        self.layout().addWidget(box)

    def save_dirty(self) -> bool:
        """Returns True if config had changed and emoji need reloading"""
        from ..config import dump_config, config_state
        logger.debug('Saving config state if changed')
        if config_state != self._initial_config:
            dump_config()
            self._initial_config = config_state
            return True
