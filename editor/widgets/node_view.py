from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QPainter, QMouseEvent, QCursor, QPixmap


class KMBNodeGraphicView(QGraphicsView):

    scene_pos_changed = pyqtSignal(int, int)

    def __init__(self,
                 graphic_scene: QGraphicsScene,
                 status_bar_msg,
                 parent=None):
        super().__init__(parent)

        self.scene = graphic_scene
        self.status_bar_msg = status_bar_msg
        # 0 is select (also edit-finished mode), 1 is move, 2 is editing.
        self.mouse_mode = 0
        self.last_scene_mouse_pos = None

        self.zoom_in_factor = 1.25
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = (0, 10)
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
        self.mouse_mode = 0
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCursor(Qt.ArrowCursor)

    def set_movable_mode(self):
        self.mouse_mode = 1
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def set_editing_mode(self, arg):
        self.mouse_mode = 2
        self.set_node_cursor()
        self.status_bar_msg(arg + ' is selected now.')

    def set_finished_mode(self):
        self.mouse_mode = 0
        self.setCursor(Qt.ArrowCursor)

    # ------------------OVERRIDES--------------------

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton or self.mouse_mode == 1:
            self.middle_mouse_button_pressed(event)
        if event.button() == Qt.LeftButton:
            if self.mouse_mode == 2:
                self.add_selected_node_item()
            else:
                self.left_mouse_button_pressed(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton or self.mouse_mode == 1:
            self.middle_mouse_button_released(event)
        if event.button() == Qt.LeftButton:
            pass
        if event.button() == Qt.RightButton:
            if self.mouse_mode == 2:
                self.set_finished_mode()

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

    # ------------------EVENT--------------------

    def middle_mouse_button_pressed(self, event):
        release_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                    Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(release_event)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                 Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fake_event)

    def middle_mouse_button_released(self, event):
        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                 Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fake_event)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def left_mouse_button_pressed(self, event):
        item = self.get_item_at_click(event)
        print(item)

    def add_selected_node_item(self):
        x, y = int(self.last_scene_mouse_pos.x()),\
               int(self.last_scene_mouse_pos.y())
        pix = QPixmap(r'X:\projects\Karken-KMB\editor\icon\nodes\activation.png')
        node = QGraphicsPixmapItem(pix)
        node.setPos(x-40, y-40)
        node.setScale(0.17)
        self.scene.addItem(node)

    # ------------------UTILS--------------------

    def get_item_at_click(self, event):
        """ Return the object that clicked on. """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def set_node_cursor(self):
        pix = QPixmap('editor/icon/cross.png').scaled(30, 30)
        self.setCursor(QCursor(pix))
