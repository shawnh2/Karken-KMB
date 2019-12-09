from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, QPropertyAnimation, QPoint, QEasingCurve

from editor.component.sidebar_button import SideBarButton
from cfg import icon


class KMBViewSideBar(QWidget):
    """ The side floating button of editor view. """
    # todo: locate function.

    LOCK_WHEEL = pyqtSignal(bool)
    ZOOM_IN = pyqtSignal(bool)   # to view
    ZOOM_OUT = pyqtSignal(bool)  # to view

    def __init__(self, parent):
        super().__init__(parent)
        self.w = 185
        self.h = 65
        self.x = 0
        self.y = 0
        self.margin_bottom = 10
        self.ani_duration = 600
        self.on_display = False
        # setup layout
        self.inner_layout = QHBoxLayout(self)
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

    def update_pos(self, width: int, height: int):
        self.x = width/2 - self.w/2
        self.y = height - self.h
        self.move(self.x, self.y + self.h)

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

    def slide_in_animation(self):
        self.on_display = True
        ani_in = QPropertyAnimation(self, b'pos', self)
        ani_in.setDuration(self.ani_duration)
        ani_in.setStartValue(QPoint(self.x, self.y + self.h))
        ani_in.setEndValue(QPoint(self.x, self.y + self.margin_bottom))
        ani_in.setEasingCurve(QEasingCurve.InOutQuad)
        ani_in.start()

    def slide_out_animation(self):
        self.on_display = False
        ani_out = QPropertyAnimation(self, b'pos', self)
        ani_out.setDuration(self.ani_duration)
        ani_out.setStartValue(QPoint(self.x, self.y + self.margin_bottom))
        ani_out.setEndValue(QPoint(self.x, self.y + self.h))
        ani_out.setEasingCurve(QEasingCurve.InOutQuad)
        ani_out.start()