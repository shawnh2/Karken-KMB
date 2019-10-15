from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt5.QtGui import QColor, QPen, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QLineF, QPointF

from cfg import LINE_WIDTH


class KMBGraphicEdge(QGraphicsPathItem):

    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge  # the wrapper of itself
        self.pos_src = [0, 0]
        self.pos_dst = [0, 0]

        self._color = QColor("#000000")
        self._color_selected = QColor("#FF0033")

        self._pen = QPen(self._color)
        self._pen.setWidthF(LINE_WIDTH)

        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(LINE_WIDTH)

        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setStyle(Qt.DashDotLine)
        self._pen_dragging.setWidthF(LINE_WIDTH)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def set_src(self, x, y):
        self.pos_src = [x, y]

    def set_dst(self, x, y):
        self.pos_dst = [x, y]

    def calc_path(self):
        raise NotImplemented("This handler drawing QPainterPath from A to B,"
                             "but never implemented.")

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

        # setup arrow drawing
        # line = QLineF(QPointF(*self.pos_src), QPointF(*self.pos_dst))
        # vec = line.unitVector()
        # vec.setLength(30)  # arrow length
        # vec.translate(QPointF(line.dx(), line.dy()))
        # n_vec = vec.normalVector()
        # n_vec.setLength(n_vec.length()*0.4)  # arrow width
        # nn_vec = n_vec.normalVector().normalVector()
        # p1 = vec.p2()
        # p2 = n_vec.p2()
        # p3 = nn_vec.p2()
        # arrow = QPolygonF([p1, p2, p3, p1])
        # # drawing both path and arrow
        # path = QPainterPath()
        # path.moveTo(*self.pos_src)
        # path.lineTo(*self.pos_dst)
        # path.addPolygon(arrow)

        painter.drawPath(self.path())
