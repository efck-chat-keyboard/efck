import logging
import os
import re
from functools import lru_cache
from pathlib import Path

from .. import IS_MACOS, IS_WIDOWS
from ..qt import *
from ..tab import Tab
from ..config import recent_emojis

logger = logging.getLogger(__name__)


# Tabs are alphabetically sorted by classname, so this puts
# it after Emoji but before Filters.
class FRecentTab(Tab):
    label = '&Recent'
    icon = QIcon()  # TODO: add an icon
    line_edit_kwargs = dict(
        placeholderText='Filter recent emoji ...',
    )
    list_view_kwargs = dict(
        flow=QListView.Flow.LeftToRight,
        isWrapping=True,
        wordWrap=True,
        verticalScrollBarPolicy=Qt.ScrollBarPolicy.ScrollBarAlwaysOn,
    )
    # Left/Right keys move the list view item selection
    line_edit_ignore_keys = {Qt.Key.Key_Left, Qt.Key.Key_Right} | Tab.line_edit_ignore_keys

    def activated(self, force_clipboard, **kwargs):
        from ..output import type_chars
        from ..config import recent_emojis, dump_recent_emojis
        text = self.view.currentIndex().data()
        if text in recent_emojis:
            recent_emojis.remove(text)
        recent_emojis.insert(0, text)
        recent_emojis[:] = recent_emojis[:50]  # keep only 50
        dump_recent_emojis(recent_emojis)
        # Update the view
        self.model.beginResetModel()
        self.model.endResetModel()
        type_chars(text, force_clipboard)
        return False

    class ListModel(QAbstractListModel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.emoji_data = ()
            self.emoji_metadata = {}  # Map emoji -> (name, alt_name, shortcode, custom_str)

        def init(self):
            logger.info('Reloading recent emoji ...')
            # Build metadata lookup from enum_emojis
            from ..emoji import enum_emojis
            for emoji_tuple in enum_emojis():
                emoji_char = emoji_tuple[0]
                metadata = emoji_tuple[1:]  # (name, alt_name, shortcode, custom_str)
                self.emoji_metadata[emoji_char] = metadata
            self.emoji_data = recent_emojis

        def rowCount(self, index):
            return len(self.emoji_data)

        def data(self, index, role):
            if role == Qt.ItemDataRole.DisplayRole:
                emoji = self.emoji_data[index.row()]
                return emoji
            if role == Qt.ItemDataRole.UserRole:
                return (self.emoji_data[index.row()],)  # tuple for consistency
            if role == Qt.ItemDataRole.ToolTipRole:
                return self.emoji_data[index.row()]

    class Model(QSortFilterProxyModel):
        filter_words = ()

        def init(self, **kwargs):
            self._model.init()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._model = FRecentTab.ListModel(parent=self)
            self.setSourceModel(self._model)

        def set_text(self, text):
            self.filter_words = text.lower().split()
            self.invalidateFilter()

        def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
            if not self.filter_words:
                return True
            emoji = self._model.emoji_data[source_row]
            # Get metadata for this emoji (name, alt_name, shortcode, custom_str)
            metadata = self._model.emoji_metadata.get(emoji, ())
            # Filter by checking if all filter words appear in any of the metadata strings
            return bool(self.first_matching_string(metadata, self.filter_words))

        @staticmethod
        def first_matching_string(strings, words) -> str:
            # First of the strings (name, alt_name, shortcode, custom_str) that contains
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
            "Symbola",
        ]
        _TEXT_OFFSET = 0
        _ICON_OFFSET = 0
        if IS_MACOS:
            ICON_FONT_FAMILY = 'Apple Color Emoji'
            _ICON_OFFSET = -5
        elif IS_WIDOWS:
            ICON_FONT_FAMILY = 'Segoe UI Emoji'
            TEXT_FONT.setFamily('Arial')
            ICON_FONT_SIZE -= 3
            _TEXT_OFFSET = 5
            _ICON_OFFSET = -7
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

        ICON_FONT_FAMILY = os.environ.get('ICON_FONT', ICON_FONT_FAMILY)

        ICON_FONT = QFont()
        ICON_FONT.setFamilies([ICON_FONT_FAMILY, *ALL_FONT_FAMILIES])

        filter_words = ()
        highlight_words = lambda _, text: text

        def set_text(self, text):
            self.filter_words = words = text.lower().split()
            find_words_re = re.compile(fr'({"|".join(map(re.escape, words))})', flags=re.I)
            self.highlight_words = lambda text: find_words_re.sub(r'<b>\1</b>', text)

        def init(self, *, config, zoom, **kwargs):
            assert .5 < zoom <= 2
            self.GRID_SIZE.scale(int(round(self.GRID_CELL_SIZE_PX * zoom)),
                                 int(round(self.GRID_CELL_SIZE_PX * zoom)),
                                 Qt.AspectRatioMode.IgnoreAspectRatio)
            self.ICON_FONT.setPixelSize(int(round(self.ICON_FONT_SIZE * zoom)))
            self.ICON_OFFSET = zoom * QPoint(0, self._ICON_OFFSET)

            self._StaticText.cache_clear()

            # Make sure the view calls sizeHint() again
            self.parent().view.reset()

        def sizeHint(self, option, index):
            return self.GRID_SIZE

        @lru_cache(5000)
        def _StaticText(self, text):
            s = QStaticText(text)
            s.setTextFormat(Qt.TextFormat.RichText if '<' in text else Qt.TextFormat.PlainText)
            s.setPerformanceHint(QStaticText.PerformanceHint.AggressiveCaching)
            s.setTextWidth(self.GRID_SIZE.width())
            s.setTextOption(QTextOption(Qt.AlignmentFlag.AlignHCenter))
            return s

        def paint(self, painter: QPainter, option, index: QModelIndex):
            self.initStyleOption(option, index)
            painter.save()
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
                painter.setPen(option.palette.color(QPalette.ColorRole.HighlightedText))

            emoji = index.data(Qt.ItemDataRole.UserRole)[0]

            text = self._StaticText(emoji)
            painter.setFont(self.ICON_FONT)
            painter.drawStaticText(option.rect.topLeft() + self.ICON_OFFSET, text)

            # No text below for recent, just the emoji

            painter.restore()

    class Options(QWidget):
        def __init__(self, *args, config, **kwargs):
            super().__init__(*args, **kwargs)
            # No options for recent tab
            self.setLayout(QVBoxLayout(self))
