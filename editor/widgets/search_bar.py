from PyQt5.QtWidgets import QLineEdit, QAction, QWidget, QVBoxLayout, QListWidget
from PyQt5.QtCore import QPropertyAnimation, QPoint, QEasingCurve, Qt
from PyQt5.QtGui import QIcon

from cfg import SS_SEARCH, icon
from lib import load_stylesheet


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
        self.width_ratio = 0.65
        self.height_ratio = 0.75
        self.slide_duration = 600
        # the query result height for body.
        self.query_height = 70

        # init widget
        self.layout = QVBoxLayout(self)
        self.search_line = KMBSearchBarLineEdit(self)
        self.search_body = KMBSearchBrowserBody(self)
        self.layout.addWidget(self.search_line, alignment=Qt.AlignTop)
        self.layout.addWidget(self.search_body, alignment=Qt.AlignBottom)
        self.search_body.setHidden(True)
        # init slots
        self.search_line.textChanged.connect(self.update_height)
        # init ui
        self.setFixedHeight(50)
        self.setStyleSheet(load_stylesheet(SS_SEARCH))

    def update_size(self, width: int, height: int):
        self.w = int(width * self.width_ratio)
        self.max_body_h = int(height * self.height_ratio)
        self.x = width / 2 - self.w / 2
        self.setFixedWidth(self.w)
        if self.on_display:
            self.move(self.x, self.y)
        else:
            self.move(self.x, -self.h)

    def update_height(self, p_str):
        n = len(p_str)
        if n == 0:
            self.search_body.setHidden(True)
            self.setFixedHeight(self.h)
        else:
            body_height = n * self.query_height
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


class KMBSearchBarLineEdit(QLineEdit):
    """ The input line of search bar. """

    def __init__(self, parent):
        super().__init__(parent)
        # init action
        self.clear_action = QAction(QIcon(icon['C_CLEAR']), '', self)
        self.clear_action.triggered.connect(self.clear_text)
        # init ui
        self.addAction(self.clear_action, QLineEdit.TrailingPosition)
        self.setPlaceholderText('Search something ...')
        self.setFocusPolicy(Qt.StrongFocus)

    def clear_text(self):
        self.setText("")

    def slide_in_actions(self):
        # act while search bar slide in.
        self.clear_text()
        self.setFocus()

    def slide_out_actions(self):
        # act while search bar slide out.
        pass


class KMBSearchBrowserBody(QListWidget):
    """ The output results of search bar. """

    def __init__(self, parent):
        super().__init__(parent)

    def slide_in_actions(self):
        # clean.
        pass

    def slide_out_actions(self):
        # disappear.
        self.setHidden(True)
