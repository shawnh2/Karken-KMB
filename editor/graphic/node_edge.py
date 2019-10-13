from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt5.QtGui import QColor, QPen, QPainterPath
from PyQt5.QtCore import Qt


class KMBGraphicEdge(QGraphicsPathItem):

    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge
        self.pos_src = [0, 0]
        self.pos_dst = [200, 100]

        self._color = QColor("#001000")
        self._color_selected = QColor("#00FF00")

        self._pen = QPen(self._color)
        self._pen.setWidthF(2.0)

        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(2.0)

        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setStyle(Qt.DashLine)
        self._pen_dragging.setWidthF(2.0)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def set_src(self, x, y):
        self.pos_src = [x, y]

    def set_dst(self, x, y):
        self.pos_dst = [x, y]

    def calc_path(self):
        raise NotImplemented("This handler drawing QPainterPath from A to B,"
                             "but never implemented.")

    def intersect_with(self, p1, p2):
        cut_path = QPainterPath(p1)
        cut_path.lineTo(p2)
        path = self.calc_path()
        return cut_path.intersects(path)

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.calc_path()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.setPath(self.calc_path())

        if self.edge.end_item is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())
