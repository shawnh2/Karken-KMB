from PyQt5.QtWidgets import QPushButton

from cfg import SS_SIDEBTN
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
        self.btn_size = 32
        # setup ui.
        self.setStatusTip(tooltip)

        press_block = ''
        check_block = ''
        if btn_checked_img:
            check_block = f'image: url({btn_checked_img});'
        if btn_pressed_img:
            press_block = f'image: url({btn_pressed_img});'
        self.setStyleSheet(load_stylesheet(SS_SIDEBTN).format(
            b_size=self.btn_size,
            i_path=btn_img,
            check_block=check_block,
            press_block=press_block
        ))
