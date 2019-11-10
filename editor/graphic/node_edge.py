import math

from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtCore import Qt

from cfg import EDGE_WIDTH, color, EDGE_DIRECT


class KMBGraphicEdge(QGraphicsPathItem):
    """ Basic edge wrapper class, call the type of edges while using. """

    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge  # the wrapper of itself
        self.type = EDGE_DIRECT  # default
        self.pos_src = [0, 0]
        self.pos_dst = [0, 0]

        self._color_io = QColor(color['EDGE_IO'])
        self._color_ref = QColor(color['EDGE_REF'])
        self._color_selected = QColor(color['EDGE_SEL'])
        self._color_hover = QColor(color['EDGE_HOVER'])

        self._pen_io = QPen(self._color_io)
        self._pen_io.setWidthF(EDGE_WIDTH)
        self._pen_ref = QPen(self._color_ref)
        self._pen_ref.setWidthF(EDGE_WIDTH)
        self._pen_ref.setStyle(Qt.DotLine)

        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(EDGE_WIDTH)

        self._pen_dragging = QPen(self._color_io)
        self._pen_dragging.setStyle(Qt.DashDotLine)
        self._pen_dragging.setWidthF(EDGE_WIDTH)

        self._mark_pen = QPen(Qt.green)
        self._mark_pen.setWidthF(EDGE_WIDTH)
        self._mark_brush = QBrush()
        self._mark_brush.setColor(Qt.green)
        self._mark_brush.setStyle(Qt.SolidPattern)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

    def set_src(self, x, y):
        self.pos_src = [x, y]

    def set_dst(self, x, y):
        self.pos_dst = [x, y]

    def set_marker_color(self, color_hex):
        self._mark_pen.setColor(QColor(color_hex))
        self._mark_brush.setColor(QColor(color_hex))
        self.update()

    def calc_path(self):
        # every type of edges are special here.
        raise NotImplemented

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.calc_path()

    def paint(self, painter, graphics_item, widget=None):
        self.setPath(self.calc_path())

        path = self.path()
        if self.edge.end_item is None:
            painter.setPen(self._pen_dragging)
            painter.drawPath(path)
        else:
            # draw direct I/O line with output mark
            if self.type == EDGE_DIRECT:
                # paint a output mark on the edge
                x1, y1 = self.pos_src
                x2, y2 = self.pos_dst
                radius = 6   # marker radius
                length = 55  # marker length
                k = math.atan2(y2 - y1, x2 - x1)
                new_x = x2 - length * math.cos(k) - EDGE_WIDTH
                new_y = y2 - length * math.sin(k) - EDGE_WIDTH
                # draw path line first
                painter.setPen(self._pen_io if not self.isSelected() else self._pen_selected)
                painter.drawPath(path)
                # draw output marker last
                painter.setPen(self._mark_pen)
                painter.setBrush(self._mark_brush)
                painter.drawEllipse(new_x, new_y, radius, radius)
            # draw ref curve line with different pen
            else:
                painter.setPen(self._pen_ref if not self.isSelected() else self._pen_selected)
                painter.drawPath(path)

    def hoverEnterEvent(self, event):
        self._pen_io.setColor(self._color_hover)
        self._pen_ref.setColor(self._color_hover)
        self.update()

    def hoverLeaveEvent(self, event):
        self._pen_io.setColor(self._color_io)
        self._pen_ref.setColor(self._color_ref)
        self.update()
