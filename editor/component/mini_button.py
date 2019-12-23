from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon

from cfg import SS_MINIBTN
from lib import load_stylesheet


class MiniSquareButton(QPushButton):
    """ A mini type of push button, that only has icon or text. """

    def __init__(self, icon: str = None, mini_size: int = 15, text: str = None):
        super().__init__()

        style_sheet = load_stylesheet(SS_MINIBTN)
        self.setStyleSheet(style_sheet.format(size=mini_size))
        if icon:
            self.setIcon(QIcon(icon))
        if text:
            self.setText(text)
