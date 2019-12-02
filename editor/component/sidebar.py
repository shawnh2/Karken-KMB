from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QApplication
from PyQt5.QtCore import pyqtSignal

from cfg import icon, SS_SIDEBTN
from lib import load_stylesheet


class SideBarButton(QPushButton):
    """ The button that exists in sidebar. """

    def __init__(self,
                 btn_img: str,
                 tooltip: str,
                 parent,
                 btn_checked_img: str = None,
                 btn_pressed_img: str = None):
        super().__init__(parent)
        # add support for both Normal and Retina screen.
        self.ratio = QApplication.desktop().screen().devicePixelRatio()
        self.btn_size = 64 // self.ratio
        # setup ui.
        self.setStatusTip(tooltip)
        press_block = ''
        check_block = ''
        if btn_checked_img:
            check_block = f'image: url({btn_checked_img});'
        if btn_pressed_img:
            press_block = f'image: url({btn_pressed_img});'
        self.setStyleSheet(load_stylesheet(SS_SIDEBTN).format(
            b_size=self.btn_size, i_path=btn_img,
            check_block=check_block, press_block=press_block
        ))


class KMBViewSideBar(QWidget):
    """ The side floating button of editor view. """
    # todo: function on button and progress bar.
    # todo: auto hide and show with animation.

    LOCK_WHEEL = pyqtSignal(bool)
    ZOOM_IN = pyqtSignal(bool)   # to view
    ZOOM_OUT = pyqtSignal(bool)  # to view

    def __init__(self, parent):
        super().__init__(parent)
        self.w = 65
        self.h = 190
        # setup layout
        self.inner_layout = QVBoxLayout(self)
        # setup buttons in sidebar
        self.lock_roll_btn = SideBarButton(
            icon['S_LOCK'], 'Disable Roll Wheel', self,
            btn_checked_img=icon['S_LOCK_CHECK']
        )
        self.zoom_in_btn = SideBarButton(
            icon['S_ZOOM_IN'], 'Zoom In View', self,
            btn_pressed_img=icon['S_ZOOM_IN_PRESS']
        )
        self.zoom_out_btn = SideBarButton(
            icon['S_ZOOM_OUT'], 'Zoom Out View', self,
            btn_pressed_img=icon['S_ZOOM_OUT_PRESS']
        )
        self.auto_locate_btn = SideBarButton(
            icon['S_LOCATE'], 'Locating', self,
            btn_pressed_img=icon['S_LOCATE_PRESS']
        )
        # setup sidebar body
        self.inner_layout.addWidget(self.lock_roll_btn)
        self.inner_layout.addWidget(self.zoom_in_btn)
        self.inner_layout.addWidget(self.zoom_out_btn)
        self.inner_layout.addWidget(self.auto_locate_btn)
        # setup ui
        self.setFixedSize(self.w, self.h)
        # setup actions
        self.lock_roll_btn.setCheckable(True)
        self.lock_roll_btn.pressed.connect(self.lock_roll_pressed)
        self.zoom_in_btn.pressed.connect(self.zoom_in_pressed)
        self.zoom_out_btn.pressed.connect(self.zoom_out_pressed)

    def lock_roll_pressed(self):
        if not self.lock_roll_btn.isChecked():
            self.LOCK_WHEEL.emit(True)
            self.lock_roll_btn.setStatusTip('Enable Roll Wheel')
        else:
            self.LOCK_WHEEL.emit(False)
            self.lock_roll_btn.setStatusTip('Disable Roll Wheel')

    def zoom_in_pressed(self):
        self.ZOOM_IN.emit(True)

    def zoom_out_pressed(self):
        self.ZOOM_OUT.emit(True)
