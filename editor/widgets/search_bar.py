from typing import Generator

from PyQt5.QtWidgets import (QLineEdit, QAction, QWidget, QVBoxLayout, QApplication,
                             QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QScrollArea)
from PyQt5.QtCore import QPropertyAnimation, QPoint, QEasingCurve, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont

from cfg import SS_SEARCH, icon, NODE_ICONx85_PATH
from lib import load_stylesheet
from editor.component.delay_timer import DelayedTimer


QUERY_HEIGHT = 70


class KMBSearchBar(QWidget):

    def __init__(self, parent, search_thread):
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
        self.search_body.close()
        # init delay timer and search thread
        self.delay_timer = DelayedTimer(self.search_line)
        self.search_thread = search_thread
        # init slots
        self.search_line.textChanged.connect(self.delay_timer.trigger)
        self.delay_timer.triggered.connect(self.do_query)
        self.search_line.FOCUS_ON_BODY.connect(self.focus_on_body)
        self.search_line.PRESS_ENTER.connect(self.do_query)
        self.search_body.FOCUS_ON_LINE.connect(self.focus_on_line)
        self.search_body.ENTER_NEW_ITEM.connect(self.recover)
        # init ui
        self.setFixedHeight(self.h)
        self.setStyleSheet(load_stylesheet(SS_SEARCH))

    def do_query(self, query_str: str):
        # begin search and updates browser body.
        if not query_str:
            self.recover()
        else:
            count = self.search_thread.search(query_str)
            generator = self.search_thread.fetchall()
            candies = self.search_thread.fetch_candies()
            self.search_body.feed_items(generator)
            self.search_body.feed_candies(candies)
            self.update_height(count)

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
            self.recover()
        else:
            body_height = (count + 1) * QUERY_HEIGHT
            if body_height > self.max_body_h:
                body_height = self.max_body_h
            self.search_body.show()
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
        self.recover()
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

    def recover(self):
        # back to where begins.
        self.search_body.clear()
        self.search_body.close()
        self.setFixedHeight(self.h)


class KMBSearchBarLineEdit(QLineEdit):
    """ The input line of search bar. """

    FOCUS_ON_BODY = pyqtSignal(bool)
    PRESS_ENTER = pyqtSignal(str)

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
        elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.PRESS_ENTER.emit(self.text())
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
    ENTER_NEW_ITEM = pyqtSignal(str, str, str, str)  # name, sort, category, args

    def __init__(self, parent):
        super().__init__(parent)
        self.setIconSize(QSize(32, 32))
        self.setViewMode(QListWidget.ListMode)
        self.setMovement(QListWidget.Static)
        self.setItemAlignment(Qt.AlignCenter)
        self.setAlternatingRowColors(True)
        self._width = self.width()
        self._candies: (int, str) = None  # like cookies, but carrying something else.

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
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.enter_item()
        else:
            event.ignore()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # update item size hint when width changed.
        if self._width != self.width():
            self._width = self.width()
            for i in range(self.count()):
                item = self.item(i)
                item.setSizeHint(QSize(self._width, QUERY_HEIGHT))
        else:
            pass

    def mouseDoubleClickEvent(self, event):
        # actions on selected item.
        self.enter_item()

    def slide_in_actions(self):
        # clean.
        self.clear()

    def slide_out_actions(self):
        pass

    def feed_items(self, items_gen: Generator):
        # clean first.
        self.clear()
        # show the result items.
        for item, from_idx, step in items_gen:
            real_item = KMBCustomQueryItem(
                *item, key_word_selection=(from_idx, step)
            )
            fake_item = QListWidgetItem(self)
            fake_item.setSizeHint(QSize(self.width(), QUERY_HEIGHT))
            self.addItem(fake_item)
            self.setItemWidget(fake_item, real_item)

    def feed_candies(self, candies: (int, str)):
        self._candies = candies

    def enter_item(self):
        # actions after choosing one item.
        item = self.itemWidget(self.currentItem())
        for _ in range(self._candies[0]):
            self.ENTER_NEW_ITEM.emit(item.name, item.sort, item.category, self._candies[1])
        # eat all the candies after entering.
        self._candies = None


class KMBCustomQueryItem(QWidget):
    """ The query item of search body. """

    def __init__(self,
                 *args: str,
                 parent=None,
                 key_word_selection: tuple = None):
        super().__init__(parent)
        self.name, self.info, self.sort, self.category = args
        self.setFixedHeight(QUERY_HEIGHT)
        # init layouts
        self.main_layout = QHBoxLayout(self)
        self.text_layout = QVBoxLayout()
        # init widgets
        # main header
        self.header = QLabel(f'<b>{self.name}</b> - {self.category}')
        if key_word_selection is not None:
            self.header.setSelection(*key_word_selection)
        # scroll sub header
        self.sub_text = ScrollableLabel(self.info)
        # icon placeholder
        self.icon = QLabel()
        self.init_icon()
        # combine
        self.text_layout.addWidget(self.header, alignment=Qt.AlignLeft)
        self.text_layout.addWidget(self.sub_text, alignment=Qt.AlignLeft)
        self.main_layout.addWidget(self.icon, alignment=Qt.AlignLeft)
        self.main_layout.addLayout(self.text_layout)
        self.main_layout.addStretch(-1)

    def init_icon(self):
        # set compatible
        pix = QPixmap(NODE_ICONx85_PATH.format(self.sort, self.name))
        ratio = QApplication.desktop().screen().devicePixelRatio()
        if ratio == 1:
            pass
        else:
            pix.setDevicePixelRatio(ratio)
        self.icon.setPixmap(pix)


class ScrollableLabel(QScrollArea):
    """ Scrollable text label. """
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        # init content
        self.font = QFont()
        self.font.setPointSize(10)
        self.label = QLabel(text)
        self.label.setFont(self.font)
        self.label.setEnabled(False)
        self.label.setStyleSheet("background: transparent")
        # init self
        self.setWidget(self.label)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
