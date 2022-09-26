import logging
from functools import lru_cache
from glob import glob
from pathlib import Path

from ..qt import *
from ..gui import ICON_DIR
from ..tab import Tab
from ..util import (
    import_module_from_file,
    import_pyinstaller_bundled_submodules,
    iter_config_dirs,
)

logger = logging.getLogger(__name__)


def load_modules():
    """Return built-in filter modules, shadowed by name by user's config-local filter modules."""
    all_modules = {}

    for mod in import_pyinstaller_bundled_submodules('efck.filters'):
        all_modules[module_basename(mod)] = mod

    for dir in iter_config_dirs('filters'):
        for file in sorted(glob(str(dir / '*.py*'))):
            logger.debug('Loading filter "%s"', file)
            mod = import_module_from_file(f'efck.filters.{Path(file).stem}', file)
            all_modules[module_basename(mod)] = mod

    # Empty user's config-local filters by the same name can shadow out builtins
    for name, mod in tuple(all_modules.items()):
        if not callable(getattr(mod, 'func', None)):
            logger.warning('Skipping invalid module "%s" from "%s"', name, mod.__spec__.origin)
            all_modules.pop(name)

    # Cache filter transformations
    for name, mod in all_modules.items():
        if name != 'zalgo':  # Except Zalgo text
            mod.func = lru_cache(3)(mod.func)

    modules = list(dict(sorted(all_modules.items())).values())
    return modules


def module_basename(module):
    name = module.__name__.rsplit('.', maxsplit=1)[1]
    return name


class FiltersTab(Tab):
    label = '&Filters'
    icon = QIcon.fromTheme('format-text-strikethrough', QIcon(QPixmap(str(ICON_DIR / 'strikethrough.png'))))
    line_edit_kwargs = dict(
        placeholderText='Enter text to transform ...',
    )
    list_view_kwargs = dict()
    line_edit_ignore_keys = Tab.line_edit_ignore_keys
    line_edit_resets_selection = False

    def activated(self, force_clipboard, **kwargs):
        from ..output import type_chars
        func = self.view.currentIndex().data(Qt.ItemDataRole.UserRole)
        text = func(self.line_edit.text())
        type_chars(text, force_clipboard)

    class Model(QAbstractListModel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.modules = ()

        def init(self):
            if not self.modules:
                self.modules = load_modules()

        def rowCount(self, index):
            return len(self.modules)

        ExampleRole = Qt.ItemDataRole.UserRole + 1

        def data(self, index, role):
            if role == Qt.ItemDataRole.DisplayRole:
                module = self.modules[index.row()]
                return module_basename(module)
            if role == Qt.ItemDataRole.UserRole:
                return self.modules[index.row()].func
            if role == self.ExampleRole:
                module = self.modules[index.row()]
                return getattr(module, 'example', None) or module_basename(module).title()

    class Delegate(QStyledItemDelegate):
        SIZE = QSize(0, 40)
        FONT_NAME = QFont()
        FONT_NAME.setPointSize(7)
        FONT_TEXT = QFont()
        FONT_TEXT.setPointSize(18)
        FONT_METRICS = QFontMetrics(FONT_TEXT)

        def sizeHint(self, option, index):
            return self.SIZE

        def paint(self, painter: QPainter, option, index: QModelIndex):
            self.initStyleOption(option, index)
            painter.save()
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
                painter.setPen(option.palette.color(QPalette.ColorRole.HighlightedText))

            func = index.data(Qt.ItemDataRole.UserRole)
            text = self.parent().line_edit.text() or index.data(FiltersTab.Model.ExampleRole)
            text = func(text)
            rect = option.rect.adjusted(2, 2, -2, -2)
            text = self.FONT_METRICS.elidedText(text, Qt.TextElideMode.ElideRight, rect.width())
            painter.setFont(self.FONT_TEXT)
            painter.drawText(rect, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft, text)

            name = index.data().replace('_', ' ')
            painter.setFont(self.FONT_NAME)
            painter.drawText(rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight, name.upper())

            painter.restore()
