from PyQt5.QtWidgets import QLineEdit, QAction, QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import QPropertyAnimation, QPoint, QEasingCurve, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon

from cfg import SS_SEARCH, icon
from lib import load_stylesheet
from editor.component.delay_timer import DelayedTimer


QUERY_HEIGHT = 50


class KMBSearchBar(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        # common
        self.h = 50  # read only
        self.w = 300
        self.x = 0
        self.y = 10  # read only
        self.max_body_h = 300
        self.margin_bottom = 10
        self.on_display = False
        self.width_ratio = 0.60   # max
        self.height_ratio = 0.75  # max
        self.slide_duration = 600

        # init widget
        self.layout = QVBoxLayout(self)
        self.search_line = KMBSearchBarLineEdit(self)
        self.search_body = KMBSearchBrowserBody(self)
        self.layout.addWidget(self.search_line, alignment=Qt.AlignTop)
        self.layout.addWidget(self.search_body, alignment=Qt.AlignBottom)
        self.search_body.setHidden(True)
        # init delay timer
        self.delay_timer = DelayedTimer(self.search_line)
        # init slots
        self.search_line.textChanged.connect(self.delay_timer.trigger)
        self.delay_timer.triggered.connect(self.do_query)
        self.search_line.FOCUS_ON_BODY.connect(self.focus_on_body)
        self.search_body.FOCUS_ON_LINE.connect(self.focus_on_line)
        # init ui
        self.setFixedHeight(50)
        self.setStyleSheet(load_stylesheet(SS_SEARCH))

    def do_query(self, query_str: str):
        # begin search and updates browser body.
        query_count = len(query_str)
        # todo: search thread
        self.update_height(query_count)

    def update_size(self, width: int, height: int):
        self.w = int(width * self.width_ratio)
        self.max_body_h = int(height * self.height_ratio)
        self.x = width / 2 - self.w / 2
        self.setFixedWidth(self.w)
        if self.on_display:
            self.move(self.x, self.y)
        else:
            self.move(self.x, -self.h)

    def update_height(self, count: int):
        if count == 0:
            self.search_body.setHidden(True)
            self.setFixedHeight(self.h)
        else:
            body_height = (count + 1) * QUERY_HEIGHT
            if not body_height > self.max_body_h:
                self.search_body.setHidden(False)
                self.search_body.setFixedHeight(body_height)
                self.setFixedHeight(self.h + body_height + self.margin_bottom)

    def slide_in_animation(self):
        # pre-actions
        self.on_display = True
        self.search_line.slide_in_actions()
        self.search_body.slide_in_actions()
        # animations
        slide_in = QPropertyAnimation(self, b'pos', self)
        slide_in.setDuration(self.slide_duration)
        slide_in.setStartValue(QPoint(self.x, -self.h))
        slide_in.setEndValue(QPoint(self.x, self.y))
        slide_in.setEasingCurve(QEasingCurve.OutBounce)
        slide_in.start()

    def slide_out_animation(self):
        # pre-actions
        self.on_display = False
        self.search_line.slide_out_actions()
        self.search_body.slide_out_actions()
        # animation
        slide_out = QPropertyAnimation(self, b'pos', self)
        slide_out.setDuration(self.slide_duration)
        slide_out.setStartValue(QPoint(self.x, self.y))
        slide_out.setEndValue(QPoint(self.x, -self.h))
        slide_out.setEasingCurve(QEasingCurve.OutCubic)
        slide_out.start()

    def focus_on_body(self):
        # set focus only if it has body.
        self.search_body.setFocus()
        self.search_body.setCurrentRow(0)

    def focus_on_line(self):
        self.search_line.setFocus()


class KMBSearchBarLineEdit(QLineEdit):
    """ The input line of search bar. """

    FOCUS_ON_BODY = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        # init action
        self.clear_action = QAction(QIcon(icon['C_CLEAR']), '', self)
        self.clear_action.triggered.connect(self.clear_text)
        # init ui
        self.addAction(self.clear_action, QLineEdit.TrailingPosition)
        self.setPlaceholderText('Search something ...')
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        # down key will change focus to browser body.
        if event.key() == Qt.Key_Down:
            self.FOCUS_ON_BODY.emit(True)
        else:
            super().keyPressEvent(event)

    def clear_text(self):
        self.setText("")

    def slide_in_actions(self):
        # act while search bar slide in.
        self.clear_text()
        self.setFocus()

    def slide_out_actions(self):
        # act while search bar slide out.
        self.clearFocus()


class KMBSearchBrowserBody(QListWidget):
    """ The output results of search bar. """

    FOCUS_ON_LINE = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        self.setIconSize(QSize(32, 32))

        self.addItem(KMBSearchBrowserBodyItem('All Results'))  # todo: this item is not selectable
        self.addItem(KMBSearchBrowserBodyItem('test1', icon['S_LOCK']))
        self.addItem(KMBSearchBrowserBodyItem('test2', icon['S_LOCK']))
        self.addItem(KMBSearchBrowserBodyItem('test3', icon['S_LOCK']))
        self.addItem(KMBSearchBrowserBodyItem('test4', icon['S_LOCK']))

        # setup ui
        self.setViewMode(QListWidget.ListMode)
        self.setMovement(QListWidget.Static)
        self.setItemAlignment(Qt.AlignCenter)
        self.setAlternatingRowColors(True)

    def focusOutEvent(self, event):
        self.clearSelection()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            # if it's top item, then focus on line.
            if self.currentRow() == 0:
                self.FOCUS_ON_LINE.emit(True)
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Down:
            if self.currentRow() == self.count() - 1:
                self.FOCUS_ON_LINE.emit(True)
            else:
                super().keyPressEvent(event)
        else:
            event.ignore()

    def slide_in_actions(self):
        # clean.
        pass

    def slide_out_actions(self):
        # disappear.
        self.setHidden(True)


class KMBSearchBrowserBodyItem(QListWidgetItem):
    """ The query item of search body. """

    def __init__(self, text: str, icon_path: str = None):
        super().__init__()
        self.setText(text)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setSizeHint(QSize(200, QUERY_HEIGHT))
            self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        else:
            self.setSelected(False)
            self.setTextAlignment(1)
