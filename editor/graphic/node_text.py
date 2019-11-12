""" An annotation item along with Node Item """

from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class KMBNodeTextItem(QGraphicsTextItem):

    def __init__(self, text, gr_parent):
        super().__init__(text, gr_parent)
        # width and height of gr_item is 85
        # show the text item under node.
        self.x = -4
        self.y = 80
        self.text = text
        self._font = QFont()
        self._font.setPointSize(11)

        # initial state is hidden
        self.setVisible(False)
        self.setPos(self.x, self.y)
        self.setFont(self._font)
        self.setDefaultTextColor(Qt.white)
        self.setAcceptHoverEvents(True)

    def __repr__(self):
        return "<NodeText {}>".format(self.text)

    def appear(self):
        self.setVisible(True)

    def disappear(self):
        self.setVisible(False)
