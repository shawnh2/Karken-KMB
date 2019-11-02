import math

from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QLine, pyqtSignal

from cfg import color


class KMBNodeGraphicScene(QGraphicsScene):

    # right menu signal, when picked up an arg item
    PICKED_ONE_ARG_TO_REF = pyqtSignal(str, int, str)  # dst id, idx, src id
    PICKED_ONE_TO_IO = pyqtSignal(str, str, str)  # dst id, I/O sign, src id
    WAS_DONE_PICKING_ONE = pyqtSignal(bool)  # pick state

    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene  # the wrapper of itself

        # settings
        self.grid_size = 20
        self.grid_squares = 5

        self._color_background = QColor(color['SCENE_BG'])
        self._color_light = QColor(color['SCENE_LIGHT'])
        self._color_dark = QColor(color['SCENE_DARK'])

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self.setBackgroundBrush(self._color_background)

    def set_graphic_scene(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def right_menu_listener(self):
        # couldn't call sender() in QGraphicsPixmapItem,
        # so add it here, emit the signal here also.
        # using objectName as a data media here.
        receive = self.sender().objectName()
        args = receive.split('-')
        if args[0] == 'REF':
            self.PICKED_ONE_ARG_TO_REF.emit(args[1], int(args[3]), args[2])
        elif args[0] == 'IO':
            self.PICKED_ONE_TO_IO.emit(args[1], args[3], args[2])
            # after picking successfully, change the dot color.
            self.scene.change_color_for_io(args[4], args[3])
        # else ...

        # if had clicked the menu item, will trigger this signal.
        # send True or False. True means had clicked,
        # False means hadn't, then will clean edge and cancel this ref.
        self.WAS_DONE_PICKING_ONE.emit(True)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            if x % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.grid_size):
            if y % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

        # draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)
