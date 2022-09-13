import logging
import os
import re
from functools import lru_cache
from pathlib import Path

from .. import IS_MACOS, IS_WIDOWS
from ..qt import *
from ..gui import ICON_DIR
from ..tab import Tab
from ..emoji import enum_emojis
from ..output import type_chars

logger = logging.getLogger(__name__)


class EmojiTab(Tab):
    label = '&Emoji'
    icon = QIcon.fromTheme('face-laugh', QIcon(QPixmap(str(ICON_DIR / 'awesome-emoji.png'))))
    line_edit_kwargs = dict(
        placeholderText='Filter emoji ...',
    )
    list_view_kwargs = dict(
        flow=QListView.Flow.LeftToRight,
        isWrapping=True,
        wordWrap=True,
    )
    # Left/Right keys move the list view item selection
    line_edit_ignore_keys = {Qt.Key.Key_Left, Qt.Key.Key_Right} | Tab.line_edit_ignore_keys

    def activated(self):
        text = self.view.currentIndex().data()
        type_chars(text)

    class ListModel(QAbstractListModel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.emoji_data = ()

        def init(self):
            logger.info('Reloading emoji ...')
            self.emoji_data = list(enum_emojis())

        def rowCount(self, index):
            return len(self.emoji_data)

        def data(self, index, role):
            if role == Qt.ItemDataRole.DisplayRole:
                emoji = self.emoji_data[index.row()][0]
                return emoji
            if role == Qt.ItemDataRole.UserRole:
                return self.emoji_data[index.row()]
            if role == Qt.ItemDataRole.ToolTipRole:
                return '\n'.join(self.emoji_data[index.row()])

    class Model(QSortFilterProxyModel):
        filter_words = ()

        def init(self):
            self._model.init()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._model = EmojiTab.ListModel(parent=self)
            self.setSourceModel(self._model)

        def set_text(self, text):
            self.filter_words = text.lower().split()
            self.invalidateFilter()

        def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
            data = self._model.emoji_data[source_row]
            return bool(self.first_matching_string(data, self.filter_words))

        @staticmethod
        def first_matching_string(strings, words) -> str:
            # First of the strings (name, alt_name, shortcode) that contains
            # ALL space-separated parts in any order
            return next((s for s in strings
                         if all(w in s for w in words)), None)

        def beginResetModel(self):
            super().beginResetModel()
            self._model.beginResetModel()

        def endResetModel(self):
            super().endResetModel()
            self._model.endResetModel()
            self.invalidateFilter()

    class Delegate(QStyledItemDelegate):
        GRID_CELL_SIZE_PX = 64
        TEXT_FONT_SIZE_PX = 8
        ICON_FONT_SIZE = GRID_CELL_SIZE_PX - 16
        GRID_SIZE = QSize(GRID_CELL_SIZE_PX, GRID_CELL_SIZE_PX)
        TEXT_FONT = QFont()
        ALL_FONT_FAMILIES = [
            'Noto Color Emoji',
            "Twitter Color Emoji",
            'Apple Color Emoji',
            'Segoe UI Emoji',
            "Joypixels",
            # Reconsider
            # "OpenMoji Color",
            "Symbola",
        ]
        _TEXT_OFFSET = 0
        _ICON_OFFSET = 0
        if IS_MACOS:
            ICON_FONT_FAMILY = 'Apple Color Emoji'
        elif IS_WIDOWS:
            ICON_FONT_FAMILY = 'Segoe UI Emoji'
            TEXT_FONT.setFamily('Arial')
            ICON_FONT_SIZE -= 3
            _TEXT_OFFSET = 5
            _ICON_OFFSET = -7  # windos magic numbers
            TEXT_FONT_SIZE_PX = 9
        else:
            ICON_FONT_FAMILY = 'Noto Color Emoji'
        TEXT_OFFSET = _TEXT_OFFSET
        ICON_OFFSET = QPoint(0, _ICON_OFFSET)

        _font_file = Path(__file__).parent.parent / 'NotoColorEmoji.ttf'
        if _font_file.is_file():
            logger.info('Loading vendored font NotoColorEmoji.ttf')
            _res = QFontDatabase.addApplicationFont(str(_font_file))
            if _res == -1:
                logger.error('Error loading vendored font.')

        # Read user's font preference from the environment
        ICON_FONT_FAMILY = os.environ.get('ICON_FONT_FAMILY', ICON_FONT_FAMILY)

        ICON_FONT = QFont()
        ICON_FONT.setFamilies([ICON_FONT_FAMILY, *ALL_FONT_FAMILIES])

        filter_words = ()
        highlight_words = lambda _, text: text

        def set_text(self, text):
            self.filter_words = words = text.lower().split()
            find_words_re = re.compile(fr'({"|".join(map(re.escape, words))})')
            self.highlight_words = lambda text: find_words_re.sub(r'<b>\1</b>', text)

        def init(self, *, zoom):
            assert .5 < zoom <= 2
            self.TEXT_FONT.setPixelSize(int(round(self.TEXT_FONT_SIZE_PX * zoom)))
            CONDENSE_TEXT_ROWS = -3
            self.GRID_SIZE.scale(int(round(self.GRID_CELL_SIZE_PX * zoom)),
                                 int(round(self.GRID_CELL_SIZE_PX * zoom +
                                           self.TEXT_FONT.pixelSize() +
                                           CONDENSE_TEXT_ROWS)),
                                 Qt.AspectRatioMode.IgnoreAspectRatio)
            self.ICON_FONT.setPixelSize(int(round(self.ICON_FONT_SIZE * zoom)))
            self.ICON_OFFSET = zoom * QPoint(0, self._ICON_OFFSET)
            self.TEXT_OFFSET = zoom * self._TEXT_OFFSET

            self._StaticText.cache_clear()

            # Make sure the view calls sizeHint() again
            # Fixes "Resetting zoom back from 200% to 100% doesn't work"
            self.parent().view.reset()

        def sizeHint(self, option, index):
            return self.GRID_SIZE

        @lru_cache(3000)
        def _StaticText(self, text):
            text = f'<div align=center>{text}</div>'
            s = QStaticText(text)
            s.setTextFormat(Qt.TextFormat.RichText)
            s.setTextWidth(self.GRID_SIZE.width())
            return s

        def paint(self, painter: QPainter, option, index: QModelIndex):
            self.initStyleOption(option, index)
            painter.save()
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
                painter.setPen(option.palette.color(QPalette.ColorRole.HighlightedText))

            data = index.data(Qt.ItemDataRole.UserRole)

            text = self._StaticText(data[0])
            painter.setFont(self.ICON_FONT)
            painter.drawStaticText(option.rect.topLeft() + self.ICON_OFFSET, text)

            text = data[1]
            if self.filter_words:
                text = EmojiTab.Model.first_matching_string(data, self.filter_words)
            text = self.highlight_words(text)
            text = self._StaticText(text)
            top_left = option.rect.topLeft() + QPoint(0, self.ICON_FONT.pixelSize() + self.TEXT_OFFSET)
            painter.setFont(self.TEXT_FONT)
            painter.setClipRect(option.rect)
            painter.drawStaticText(top_left, text)

            painter.restore()

    class Options(QGroupBox):
        def __init__(self, *args, config, **kwargs):
            super().__init__('Filter Emoji', *args, **kwargs)
            self.setLayout(QHBoxLayout(self))
            listviews = {}
            filter_label = lambda x: re.sub(r' (skin tone|hair)', '', x)

            def on_changed(group_name):
                selected = {i.row() for i in
                            listviews[group_name].selectionModel().selectedIndexes()}
                # Sync options directly with the config state
                for i, f in enumerate(config[group_name]):
                    config[group_name][f] = int(i in selected)
                logger.debug('Emoji filter selected: %s %s', group_name, selected)

            for group_name, filters in config.items():
                group_box = QWidget()
                layout = QVBoxLayout(group_box)
                layout.setContentsMargins(0, 0, 0, 0)
                group_box.setLayout(layout)
                self.layout().addWidget(group_box)

                label = QLabel(f'&{group_name}', self, styleSheet="font-weight: bold")
                lst = QListWidget(
                    parent=self,
                    selectionMode=QListWidget.SelectionMode.MultiSelection,
                    itemSelectionChanged=lambda *_, group_name=group_name: on_changed(group_name),
                )
                label.setBuddy(lst)
                group_box.layout().addWidget(label)
                group_box.layout().addWidget(lst)
                listviews[group_name] = lst
                lst.blockSignals(True)
                for i, (k, v) in enumerate(filters.items()):
                    li = QListWidgetItem(filter_label(k))
                    lst.addItem(li)
                    li.setToolTip(k)
                    li.setSelected(bool(v))  # This needs to come after item is added
                lst.blockSignals(False)
