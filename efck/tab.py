from .qt import *
from .gui import _TabPrivate


class Tab(_TabPrivate):
    label = '&Tab'
    icon = QIcon()
    line_edit_kwargs = {}
    list_view_kwargs = {}
    line_edit_ignore_keys = {
        Qt.Key.Key_Up, Qt.Key.Key_Down,
        Qt.Key.Key_PageUp, Qt.Key.Key_PageDown,
        Qt.Key.Key_Home, Qt.Key.Key_End,
    }
    line_edit_resets_selection = True
    activation_can_fail = False

    class View(QListView):
        """Override this if you need to hook into stuff like keyPressEvent() ..."""

    class Model(QAbstractItemModel):
        """

        """

        # In addition to methods below, you need to override Qt methods data() and rowCount().
        # See: https://doc.qt.io/qt/qabstractitemmodel.html

        def init(self):
            """"""
        def set_text(self, text):
            """"""

    class Delegate(QStyledItemDelegate):
        """

        """
        def init(self, *, zoom=1):
            """
            """
        def set_text(self, text):
            """"""
        # Additionally, you need to override Qt method paint().
        # See: https://doc.qt.io/qt/qstyleditemdelegate.html

    class Options(QGroupBox):
        """"""
        def __init__(self, *, config, parent):
            super().__init__(parent=parent)

    def activated(self):
        """"""

    line_edit: QLineEdit
    model: Model
    view: View
    delegate: Delegate
