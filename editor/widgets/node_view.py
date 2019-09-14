from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QApplication
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QPainter, QMouseEvent, QCursor, QPixmap

from editor.widgets.node_item import KMBNodeItem


MOUSE_SELECT = 0
MOUSE_MOVE = 1
MOUSE_EDIT = 2
NODE_SELECTED = 3


class KMBNodeGraphicView(QGraphicsView):

    scene_pos_changed = pyqtSignal(int, int)

    def __init__(self,
                 graphic_scene: QGraphicsScene,
                 status_bar_msg,
                 parent=None):
        super().__init__(parent)

        self.scene = graphic_scene
        self.status_bar_msg = status_bar_msg
        self.mode = MOUSE_SELECT
        self.last_scene_mouse_pos = None
        self.current_node_item_name = None

        self.zoom_in_factor = 1.25
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = (0, 8)
        self.zoom_clamp = True

        self.init_ui()
        self.setScene(self.scene)

    def init_ui(self):
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.HighQualityAntialiasing |
                            QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # default drag mode
        self.setDragMode(QGraphicsView.RubberBandDrag)

    # ------------------MODE--------------------

    def set_select_mode(self):
        self.mode = MOUSE_SELECT
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCursor(Qt.ArrowCursor)

    def set_movable_mode(self):
        self.mode = MOUSE_MOVE
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def set_editing_mode(self, arg):
        self.mode = MOUSE_EDIT
        self.current_node_item_name = arg
        self.set_edit_node_cursor()
        self.status_bar_msg(arg + ' is selected now.')

    # ------------------OVERRIDES--------------------

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton or self.mode == MOUSE_MOVE:
            self.middle_mouse_button_pressed(event)
        elif event.button() == Qt.LeftButton:
            self.left_mouse_button_pressed(event)
        elif event.button() == Qt.RightButton:
            self.right_mouse_button_pressed(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton or self.mode == MOUSE_MOVE:
            self.middle_mouse_button_released(event)
        elif event.button() == Qt.LeftButton:
            self.left_mouse_button_released(event)
        elif event.button() == Qt.RightButton:
            self.right_mouse_button_released(event)
        else:
            super().mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        # emit pos changed signal
        self.last_scene_mouse_pos = self.mapToScene(event.pos())
        self.scene_pos_changed.emit(
            int(self.last_scene_mouse_pos.x()),
            int(self.last_scene_mouse_pos.y())
        )

        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        zoom_out_factor = 1 / self.zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoom_step

        clamped = False
        if self.zoom < self.zoom_range[0]:
            self.zoom, clamped = self.zoom_range[0], True
        if self.zoom > self.zoom_range[1]:
            self.zoom, clamped = self.zoom_range[1], True

        # set the scene scale
        if not clamped or self.zoom_clamp is False:
            self.scale(zoom_factor, zoom_factor)

    def keyPressEvent(self, event):
        pass

    # ------------------EVENT--------------------

    def middle_mouse_button_pressed(self, event):
        release_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                    Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(release_event)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                 Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())

        # if it's under move mode then continue this.
        if self.mode == MOUSE_MOVE:
            self.set_movable_mode()

        super().mousePressEvent(fake_event)

    def middle_mouse_button_released(self, event):
        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                 Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fake_event)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        if self.mode == MOUSE_MOVE:
            self.set_movable_mode()

    def left_mouse_button_pressed(self, event):
        if self.mode == MOUSE_EDIT:
            self.add_selected_node_item()

        else:
            item = self.get_item_at_click(event)
            # last_lmb_click_scene_pos = self.mapToScene(event.pos())

            if hasattr(item, 'node') or item is None:
                if event.modifiers() & Qt.ShiftModifier:
                    event.ignore()
                    fake_event = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                             Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                             event.modifiers() | Qt.ControlModifier)
                    super().mousePressEvent(fake_event)
                    return

            if item is None:
                if event.modifiers() & Qt.ControlModifier:
                    fake_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                             Qt.LeftButton, Qt.NoButton, event.modifiers())
                    super().mouseReleaseEvent(fake_event)
                    QApplication.setOverrideCursor(Qt.CrossCursor)
                    return

            super().mousePressEvent(event)

    def left_mouse_button_released(self, event):
        item = self.get_item_at_click(event)

        if hasattr(item, "node") or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                         Qt.LeftButton, Qt.NoButton,
                                         event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fake_event)
                return

        super().mouseReleaseEvent(event)

    def right_mouse_button_pressed(self, event):
        pass

    def right_mouse_button_released(self, event):
        # it will cancel all the mode and back to select mode.
        self.set_select_mode()

    # ------------------UTILS--------------------

    def get_item_at_click(self, event):
        """ Return the object that clicked on. """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def add_selected_node_item(self):
        x, y = int(self.last_scene_mouse_pos.x()),\
               int(self.last_scene_mouse_pos.y())
        node = KMBNodeItem(self.scene,
                           self.current_node_item_name)
        node.set_pos(x, y)

    def set_edit_node_cursor(self):
        pix = QPixmap('editor/icon/cross.png').scaled(30, 30)
        self.setCursor(QCursor(pix))
