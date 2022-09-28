from .qt import *
from .gui import _TabPrivate


class Tab(_TabPrivate):
    """
    This is the tab base. You create a tab by extending this class
    and define/override below properties.
    """
    #
    # Init properties
    #
    label = '&Tab'                #: Label with Alt+Letter mnemonic
    icon = QIcon()                #: Icon
    line_edit_kwargs = {}         #: Top QLineEdit's properties
    list_view_kwargs = {}         #: Main QListView's properties

    #: QLineEdit should ignore these keys as they are sent to the main
    #: app to handle. Such as Left/Right keys used to select the item
    #: in multi-column main QListViews
    line_edit_ignore_keys = {
        Qt.Key.Key_Up, Qt.Key.Key_Down,
        Qt.Key.Key_PageUp, Qt.Key.Key_PageDown,
        Qt.Key.Key_Home, Qt.Key.Key_End,
    }

    #: Typing new letters into the QLineEdit may reset selection
    #: (current index) of the QListView on the Emoji tab, but may
    #: not reset the index on the Filters tab, because the user
    #: would likely want to apply the same, selected filter.
    line_edit_resets_selection = True

    #: Use this if the QListView activation method (i.e. upon pressing
    # Enter key) can still fail or be cancelled by a user. This is
    #: used in Gifs tab where a QDrag (DND) operation can be canceled
    #: (e.g. by dropping or clicking back on our window).
    activation_can_fail = False

    class View(QListView):
        """
        This is the app's main view on each tab.
        Override this if you need to hook into stuff like `keyPressEvent()`.
        """

    class Model(QAbstractItemModel):
        """
        This is the QAbstractItemModel of the underlying data.
        See Qt docs for details:
        https://doc.qt.io/qt-6/model-view-programming.html

        In addition to methods below, you need to override
        Qt methods `data()` and `rowCount()`. See:
        https://doc.qt.io/qt/qabstractitemmodel.html
        """
        def init(self, config: dict, **kwargs):
            """
            Called when tab is first shown or when program options
            were reconfigured.
            """

        def set_text(self, text: str):
            """
            Called after a timeout tied on QLineEdit.textChanged signal.
            """

    class Delegate(QStyledItemDelegate):
        """
        Override this to customize the painting and presentation of
        View's items.

        In addition to methods below, you need to override
        Qt method `paint()`. See:
        https://doc.qt.io/qt/qstyleditemdelegate.html
        """
        def init(self, *, config: dict, zoom: float = 1, **kwargs):
            """
            Called when tab is first shown or when program options
            are reconfigured.
            """

        def set_text(self, text):
            """
            Called after a timeout tied on QLineEdit.textChanged signal.
            """

    class Options(QWidget):
        """
        The options widget for this tab. The widget should lay
        itself out in the constructor. The widget receives its namespace
        of the config dict as the first parameter and should simply
        update it in-place upon user's interaction with the widget's toggles.
        """
        def __init__(self, *, config: dict, parent: QWidget):
            super().__init__(parent=parent)

    def activated(self, force_clipboard, **kwargs) -> bool:
        """
        This is called on `View.activated` signal / Enter key press handler.
        It "does" the chosen action.
        If `Tab.activation_can_fail` above is True and if this function
        returns a True-ish value (error), the activation of the item is
        considered canceled and the app is back in idle state.
        """

    # References to instances of above types. Can be used to refer
    # to one another in methods like `activated()`, but watch out.
    line_edit: QLineEdit  #:
    model: Model          #:
    view: View            #:
    delegate: Delegate    #:
