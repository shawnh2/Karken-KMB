""" Some class like QGraphicPixmapItem could not animated by QPropertyAnimation,
In PyQt5, it doesn't allow double inheritance, so cannot implement a class that
inherits from QGraphicsPixmapItem and QGraphicsObject. So the better way is to
take over its attribute that you want to animate with.

Thanks to: https://stackoverflow.com/questions/57311232/animate-a-qgraphicspixmapitem
"""

from PyQt5.QtCore import QObject, QPointF, pyqtSignal, pyqtProperty


class GrPosManager(QObject):
    """ Take over the pos attr in gr_node. """

    POS_CHANGED = pyqtSignal(QPointF)

    def __init__(self, init_pos: QPointF, parent=None):
        super().__init__(parent)
        self._pos = init_pos

    @pyqtProperty(QPointF, notify=POS_CHANGED)
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, v):
        self._pos = v
        self.POS_CHANGED.emit(self._pos)
