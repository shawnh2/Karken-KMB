import math

from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt5.QtGui import QColor, QPen, QPainterPath, QPolygonF, QLinearGradient, QBrush
from PyQt5.QtCore import Qt, QLineF, QPointF, QPoint

from cfg import EDGE_WIDTH, color


class KMBGraphicEdge(QGraphicsPathItem):
    """ Basic edge wrapper class, call the type of edges while using. """

    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge  # the wrapper of itself
        self.pos_src = [0, 0]
        self.pos_dst = [0, 0]

        self._color = QColor(color['EDGE'])
        self._color_selected = QColor(color['EDGE_SEL'])

        self._pen = QPen(self._color)
        self._pen.setWidthF(EDGE_WIDTH)

        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(EDGE_WIDTH)

        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setStyle(Qt.DashDotLine)
        self._pen_dragging.setWidthF(EDGE_WIDTH)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def set_src(self, x, y):
        self.pos_src = [x, y]

    def set_dst(self, x, y):
        self.pos_dst = [x, y]

    def calc_path(self):
        # every type of edges are special here.
        raise NotImplemented

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
