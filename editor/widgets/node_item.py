from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem

"""class KMBNodeItem(QGraphicsItem):
    
    def __init__(self, scene):
        self.setFlag()"""


class KMBGraphicNodeItem(QGraphicsPixmapItem):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

