""" An annotation item along with Node Item """

from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtCore import Qt


class KMBNodeTextItem(QGraphicsTextItem):

    def __init__(self, text, gr_parent):
        super().__init__(text, gr_parent)
        # width and height of gr_item is 85
        # show the text item under node.
        self.x = 24 - len(text) if len(text) < 15 else 0
        self.y = 80
        self.setPos(self.x, self.y)
        self.setDefaultTextColor(Qt.white)
        self.setFlag(QGraphicsTextItem.ItemIsMovable,
                     QGraphicsTextItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.setDefaultTextColor(Qt.darkGray)

    def hoverLeaveEvent(self, event):
        self.setDefaultTextColor(Qt.white)
