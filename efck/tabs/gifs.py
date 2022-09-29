import atexit
import json
import locale
import logging
import os
import re
import uuid
from collections import namedtuple
from contextlib import contextmanager
from functools import lru_cache
from tempfile import NamedTemporaryFile
from urllib.parse import quote

from .. import IS_MACOS, __website__
from ..qt import *
from ..gui import ICON_DIR, fire_after
from ..tab import Tab

logger = logging.getLogger(__name__)


@lru_cache(1)
def _anon_id():
    from hashlib import sha256
    return sha256(b'efck' + str(uuid.getnode()).encode('utf-8')).hexdigest()


class _Request(QNetworkRequest):
    def __init__(self, url):
        super().__init__(QUrl(url))
        self.setAttribute(QNetworkRequest.Attribute.Http2AllowedAttribute, True)
        self.setAttribute(QNetworkRequest.Attribute.HttpPipeliningAllowedAttribute, True)
        self.setHeader(
            QNetworkRequest.KnownHeaders.UserAgentHeader,
            f'{QApplication.instance().applicationName()} ({__website__})')


class _TenorDownloader(QNetworkAccessManager):
    MEDIA = 'tinygif'
    URL = ('https://g.tenor.com/v1/search?'
           '&q={query}'
           '&locale={locale}'
           '&pos={{pos}}'
           '&limit=4'
           '&media_filter={media}'
           '&anon_id={anon_id}'
           '&key=LIVDSRZULELA')
    MAX_RESULTS = 20

    def __init__(self, parent, query, locales, gif_downloader):
        super().__init__(parent=parent)
        self.finished.connect(self._on_reply)
        self.setAutoDeleteReplies(True)
        self._pending_requests = {}
        self._urls = [self.URL.format(locale=lc, query=query, media=self.MEDIA,
                                      anon_id=_anon_id())
                      for lc in locales]
        for url in self._urls:
            self.get(url.format(pos=''))
        self._gif_downloader = gif_downloader
        self._gif_downloader.finished.connect(
            lambda reply: self._pending_requests.pop(reply.request().url().toString(), None))
        self._next_pos = 0
        self._seen_urls = set()

    def get(self, url):
        logger.debug('Get "%s"', url)
        self._pending_requests[url] = 1
        super().get(_Request(url))

    def _on_reply(self, reply: QNetworkReply):
        try:
            assert 'g.tenor.com' == reply.url().host(), reply.url()
            self._pending_requests.pop(reply.request().url().toString(), None)
            obj = json.loads(reply.readAll().data().decode('utf-8'))
            for result in obj['results']:
                url = result['media'][0][self.MEDIA]['url']
                url = url.split('?')[0]
                if url not in self._seen_urls:
                    self._pending_requests[url] = 1
                    self._gif_downloader.get(_Request(url))
                    self._seen_urls.add(url)

            self._next_pos = next_pos = int(float(obj['next']))
            if next_pos > self.MAX_RESULTS:
                self._next_pos = 0
            logger.debug('Fetched first %d gifs', next_pos)
        except Exception as e:
            vars = locals().copy()
            vars.pop('self')
            logger.error('Unexpected Tenor reply: %s (locals: %s)', e, vars)

    def can_fetch_more(self):
        return self._next_pos and not self._pending_requests

    def fetch_more(self):
        if not self.can_fetch_more():
            return False
        logger.debug('Fetching Tenor results from position %d', self._next_pos)
        for url in self._urls:
            self.get(url.format(pos=self._next_pos))


class _GiphyDownloader(QNetworkAccessManager):
    URL = ('https://api.giphy.com/v1/gifs/search?'
           '&q={query}'
           '&lang={lang}'
           '&offset={{offset}}'
           '&limit=4'
           '&bundle=messaging_non_clips'
           '&random_id={anon_id}'
           # '&api_key=5ntgdFsiSKoulJwLvuOo6C4Ft3ZNKyaD')
           # From https://cs.github.com/Superhero-com/superhero-ui/blob/master/.env?q=giphy+api_key#L13
           # '&api_key=P16yBDlSeEfcrJfp1rwnamtEZmQHxHNM')
           # From https://cs.github.com/HackerYou/fs-vue-starter/blob/master/steps.md?q=giphy+api+key#L8
           '&api_key=al6hW8enSGMDZsMRW83CUYjyhCDhFiPG')
    MAX_RESULTS = 20

    def __init__(self, parent, query, locales, gif_downloader):
        super().__init__(parent=parent)
        self.finished.connect(self._on_reply)
        self.setAutoDeleteReplies(True)
        self._pending_requests = {}
        langs = [i.split('_')[0] for i in locales]
        self._urls = [self.URL.format(lang=lang, query=query,
                                      anon_id=_anon_id())
                      for lang in langs]
        for url in self._urls:
            self.get(url.format(offset=''))
        self._gif_downloader = gif_downloader
        self._gif_downloader.finished.connect(
            lambda reply: self._pending_requests.pop(reply.request().url().toString(), None))
        self._next_pos = 0
        self._seen_urls = set()

    def get(self, url):
        logger.debug('Get "%s"', url)
        self._pending_requests[url] = 1
        super().get(_Request(url))

    def _on_reply(self, reply: QNetworkReply):
        try:
            self._pending_requests.pop(reply.request().url().toString(), None)
            obj = json.loads(reply.readAll().data().decode('utf-8'))
            for result in obj['data']:
                url = result['images']['fixed_height']['url']
                id = re.search(r'(?<=/media/)[^/]+', url).group()
                url = f'https://i.giphy.com/media/{id}/200.gif'
                if url not in self._seen_urls:
                    self._pending_requests[url] = 1
                    self._gif_downloader.get(_Request(url))
                    self._seen_urls.add(url)

            pagination = obj['pagination']
            self._next_pos = next_pos = int(pagination['offset']) + int(pagination['count'])
            if next_pos > self.MAX_RESULTS or next_pos >= obj['pagination']['total_count']:
                self._next_pos = 0
            logger.debug('Fetched first %d gifs', next_pos)
        except Exception as e:
            vars = locals().copy()
            vars.pop('self')
            logger.error('Unexpected Giphy reply: %s (locals: %s)', e, vars)

    def can_fetch_more(self):
        return self._next_pos and not self._pending_requests

    def fetch_more(self):
        if not self.can_fetch_more():
            return False
        logger.debug('Fetching Giphy results from position %d', self._next_pos)
        for url in self._urls:
            self.get(url.format(offset=self._next_pos))


GifItem = namedtuple('GifItem', ['url', 'movie', 'buffer'])


def _remove_file(filename):
    logger.debug('Remove "%s"', filename)
    try:
        os.remove(filename)
    except Exception as exc:
        # os.remove() may raise on Widows if file is "in use"
        logger.debug('Cannot remove "%s": %s', filename, exc)


class GifsTab(Tab):
    label = '&GIFs'
    icon = QIcon.fromTheme('image-x-generic', QIcon(QPixmap(str(ICON_DIR / 'gifs.png'))))
    line_edit_kwargs = dict(
        placeholderText='Enter search text ...',
    )
    list_view_kwargs = dict(
        verticalScrollBarPolicy=Qt.ScrollBarPolicy.ScrollBarAlwaysOn,
        uniformItemSizes=False,
        spacing=5,
        flow=QListView.Flow.LeftToRight,
        isWrapping=True,
    )
    # Left/Right keys move the GIF view item selection
    line_edit_ignore_keys = {Qt.Key.Key_Left, Qt.Key.Key_Right} | Tab.line_edit_ignore_keys

    activation_can_fail = True

    def activated(self, force_clipboard, **kwargs):
        gif: GifItem = self.model.gifs[self.view.currentIndex().row()]
        gif_bytes = gif.buffer[0].data()

        if force_clipboard:
            data = QMimeData()
            data.setData('image/gif', gif_bytes)
            # Data copied to clipboard remains in the clipboard only while the app,
            # this app, is running. This instructs the clipboard manager (in KDE?)
            # to copy and parent the image. See:
            # https://gist.github.com/springzfx/f881dff2d1c89efbfe59cfc288e09462
            # https://github.com/flameshot-org/flameshot/issues/2848#issuecomment-1199796142
            # https://cs.github.com/?q=x-kde-force-image-copy
            data.setData('x-kde-force-image-copy', b'')

            data.setUrls([QUrl(gif.url)])
            QApplication.instance().clipboard().setMimeData(data, QClipboard.Mode.Clipboard)
            QApplication.instance().processEvents()

        # Add the local GIF file into the drag and drop buffer. See:
        # https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API/Recommended_drag_types#dragging_files
        with NamedTemporaryFile(prefix=QApplication.instance().applicationName() + '-',
                                suffix='.gif', delete=False) as fd:
            fd.write(gif_bytes)
            filename = fd.name
        atexit.register(_remove_file, filename)
        logger.debug('Save "%s" into "%s"', gif.url, filename)

        data = QMimeData()
        data.setData('image/gif', gif_bytes)
        data.setUrls([QUrl.fromLocalFile(filename)])

        app = self.nativeParentWidget()

        @contextmanager
        def shade_effect():
            nonlocal app
            opacity = app.windowOpacity()
            app.setDisabled(True)
            app.setWindowOpacity(.5)
            yield
            app.setDisabled(False)
            app.setWindowOpacity(opacity)

        drag = QDrag(self)
        drag.setMimeData(data)
        drag.setPixmap(QPixmap(filename).scaledToHeight(100))
        logger.debug('Waiting for drag-and-drop action ...')

        with shade_effect():
            drop_action = drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)
            logger.info('Drop action=%s', drop_action)
            if drop_action == Qt.DropAction.IgnoreAction and \
                    not IS_MACOS:  # Always =IgnoreAction on macOS
                return str(drop_action)

        app.close()
        QApplication.instance().processEvents()

        # Wait for the file to be picked by the target app before removing it on quit
        logger.debug('Waiting some seconds ...')
        QThread.msleep(3000)

    class View(QListView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._pos = None

        def mousePressEvent(self, event: QMouseEvent):
            super().mousePressEvent(event)
            pos = event_position(event)
            if event.button() == Qt.MouseButton.LeftButton and self.indexAt(pos).isValid():
                self._pos = pos

        def mouseReleaseEvent(self, event: QMouseEvent):
            super().mouseReleaseEvent(event)
            self._pos = None

        def mouseMoveEvent(self, event: QMouseEvent):
            if not (event.buttons() & Qt.MouseButton.LeftButton):
                return
            if not self._pos or (event_position(event) - self._pos).manhattanLength() < QApplication.startDragDistance():
                return
            self.parent().nativeParentWidget().on_activated()

        def resizeEvent(self, event: QResizeEvent):
            fire_after(self, 'timer_resize_movies', self.model().resize_movies, 400)

    class Model(QAbstractListModel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.gifs: list[GifItem] = []
            self._gif_urls = set()
            self._gif_downloader = gif_downloader = QNetworkAccessManager(self)
            gif_downloader.finished.connect(self._on_gif_reply)
            gif_downloader.setAutoDeleteReplies(True)
            self._downloaders = []

        def init(self, **kwargs):
            self._reset_model()

        def rowCount(self, index):
            return len(self.gifs)

        def canFetchMore(self, parent: QModelIndex) -> bool:
            scrollbar = self.parent().view.verticalScrollBar()
            N_STEPS_NEAR = 10
            is_near_bottom = scrollbar.value() + N_STEPS_NEAR > scrollbar.maximum()
            return is_near_bottom and any(dl.can_fetch_more() for dl in self._downloaders)

        def fetchMore(self, parent: QModelIndex):
            for dl in self._downloaders:
                dl.fetch_more()

        def data(self, index, role):
            if role == Qt.ItemDataRole.DecorationRole:
                pixmap: QPixmap = self.gifs[index.row()].movie.currentPixmap()
                return pixmap
            if role == Qt.ItemDataRole.SizeHintRole:
                pixmap: QPixmap = self.gifs[index.row()].movie.currentPixmap()
                return QSize(pixmap.width(), pixmap.height())
            if role == Qt.ItemDataRole.ToolTipRole:
                return self.gifs[index.row()].url

        def _reset_model(self):
            logger.debug('Resetting model')
            self._downloaders.clear()
            self.beginResetModel()
            self.gifs.clear()
            self._gif_urls.clear()
            self.endResetModel()

        def resize_movies(self):
            for item in self.gifs:
                self._resize_movie(item.movie)

        def _resize_movie(self, movie: QMovie):
            movie.start()  # Need movie started for currentPixmap(). This is easier than keeping with assertions.
            pixmap = movie.currentPixmap()
            GIF_MAX_HEIGHT = 220  # ~Corresponds to Tenor 'tinygif' and Giphy 'fixed_height'
            if pixmap.height() > GIF_MAX_HEIGHT:
                pixmap = pixmap.scaledToHeight(GIF_MAX_HEIGHT)
                movie.setScaledSize(QSize(pixmap.width(), pixmap.height()))

        def _on_gif_reply(self, reply: QNetworkReply):
            url = reply.url().toString()
            assert url.endswith('.gif'), url
            if url in self._gif_urls:
                # Assuming we do search queries for multiple locales, we
                # could have processed this GIF via search with another locale
                return
            self._gif_urls.add(url)

            def frame_changed(_frame_number, *, _row=len(self.gifs)):
                mi = self.index(_row, 0)
                self.dataChanged.emit(mi, mi, [Qt.ItemDataRole.DecorationRole])

            barr = reply.readAll()
            buf = QBuffer(barr)
            movie = QMovie()
            movie.setDevice(buf)
            movie.frameChanged.connect(frame_changed)
            movie.start()
            self._resize_movie(movie)

            self.beginInsertRows(QModelIndex(), len(self.gifs), len(self.gifs) + 1)
            self.gifs.append(GifItem(url, movie, (barr, buf)))
            self.endInsertRows()
            # Select first item
            if len(self.gifs) == 1:
                self.parent().view.selectionModel().setCurrentIndex(
                    self.index(0, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)

        def set_text(self, text):
            self._reset_model()

            query = quote(text)
            locales = {QLocale.system().name(), locale.getdefaultlocale()[0]} - {None}  # None on "C" locale
            if not any(lc.startswith('en') for lc in locales):
                locales.add('en_US')

            self._downloaders.append(_TenorDownloader(self, query, locales, self._gif_downloader))
            self._downloaders.append(_GiphyDownloader(self, query, locales, self._gif_downloader))

    class Options(QWidget):
        def __init__(self, *args, config, **kwargs):
            super().__init__(*args, **kwargs, focusPolicy=Qt.FocusPolicy.NoFocus)
            self.setLayout(QHBoxLayout(self))
            self.layout().addWidget(QLabel(pixmap=QPixmap(str(ICON_DIR / 'PB_tenor_logo_blue_vertical.png'))))
            self.layout().addWidget(QLabel(pixmap=QPixmap(str(ICON_DIR / 'Poweredby_100px-White_VertLogo.png'))))

    class Delegate(QStyledItemDelegate):
        HIGHLIGHT_PEN = QPen(QApplication.instance().palette().highlight(), 12,
                             Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap, Qt.PenJoinStyle.MiterJoin)
        BORDER_PEN = QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap, Qt.PenJoinStyle.MiterJoin)

        def paint(self, painter: QPainter, option, index: QModelIndex):
            self.initStyleOption(option, index)
            painter.save()

            if option.state & QStyle.StateFlag.State_Selected:
                painter.setPen(self.HIGHLIGHT_PEN)
                painter.drawRect(option.rect)
                painter.setPen(self.BORDER_PEN)
                painter.drawRect(option.rect)

            pixmap = index.data(Qt.ItemDataRole.DecorationRole)
            painter.drawPixmap(option.rect.topLeft(), pixmap)
            painter.restore()
