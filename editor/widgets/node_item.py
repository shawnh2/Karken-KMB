from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


NODE_ICON_PATH = 'editor/icon/nodesx85/{}.png'

class KMBNodeItem():

    def __init__(self, scene, node_name):
        self.scene = scene
        self.node = KMBGraphicNodeItem(self, node_name)

        self.scene.addItem(self.node)

    def set_pos(self, x, y):
        self.node.set_pos(x, y)


class KMBGraphicNodeItem(QGraphicsPixmapItem):

    def __init__(self, node, name, parent=None):
        super().__init__(parent)

        self.node = node
        self.pix = QPixmap(NODE_ICON_PATH.format(name))
        self.current_pos = None

        self.setPixmap(self.pix)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def set_pos(self, x, y):
        dis = 85 / 2
        self.setPos(x - dis, y - dis)
