from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap

from cfg import NODE_ICONx85_PATH


class KMBNodeGraphicItem(QGraphicsPixmapItem):

    def __init__(self, node, name, parent=None):
        super().__init__(parent)

        self.node = node  # the wrapper of itself
        self.name = name
        self.pix = QPixmap(NODE_ICONx85_PATH.format(self.name))
        self.current_pos = None

        self.width = 85
        self.height = 85

        self.setPixmap(self.pix)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def __str__(self):
        return f"<KMBNodeGrItem at {hex(id(self))}>"

    def set_pos(self, x, y):
        dis = self.width / 2
        self.setPos(x - dis, y - dis)
