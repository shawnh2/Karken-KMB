from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap


NODE_ICON_PATH = 'lib/icon/nodesx85/{}.png'


class KMBNodeGraphicItem(QGraphicsPixmapItem):

    def __init__(self, node, name, parent=None):
        super().__init__(parent)

        self.node = node
        self.name = name
        self.pix = QPixmap(NODE_ICON_PATH.format(self.name))
        self.current_pos = None

        self.setPixmap(self.pix)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def set_pos(self, x, y):
        dis = 85 / 2
        self.setPos(x - dis, y - dis)
