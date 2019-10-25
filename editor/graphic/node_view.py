from PyQt5.QtWidgets import QGraphicsView, QApplication
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QPainter, QMouseEvent, QCursor, QPixmap

from editor.graphic.node_item import KMBNodeGraphicItem
from editor.graphic.node_edge import KMBGraphicEdge
from editor.wrapper.wrap_item import KMBNodeItem
from editor.wrapper.warp_edge import KMBEdge
from editor.component.edge_type import KMBGraphicEdgeDirect
from cfg import icon, EDGE_CURVES, EDGE_DIRECT
from lib import debug


MOUSE_SELECT = 0
MOUSE_MOVE = 1
MOUSE_EDIT = 2

NODE_SELECTED = 3
NODE_DELETE = 4

NODE_CONNECT = 5
EDGE_DRAG = 6


class KMBNodeGraphicView(QGraphicsView):

    # ------------------SIGNALS--------------------

    # show the changing position in status bar.
    scene_pos_changed = pyqtSignal(int, int)            # x, y coord
    # the necessary signal to add a new node in scene.
    add_new_node_item = pyqtSignal(str, str, str, int)  # name, type, id, count
    # pass the id of selected node item to edit.
    selected_node_item = pyqtSignal(str)                # id or state
    selected_delete_node = pyqtSignal(str)              # id
    # pop up the right menu of clicked node,
    # also emit the src node id along with.
    pop_up_right_menu = pyqtSignal(str)                 # dst id

    # ------------------INIT--------------------

    def __init__(self,
                 graphic_scene,
                 status_bar_msg,
                 parent=None):
        super().__init__(parent)

        self.gr_scene = graphic_scene
        self.status_bar_msg = status_bar_msg
        self.mode = MOUSE_SELECT
        self.edge_type = None
        self.has_chosen_from_rm = False
        self.last_scene_mouse_pos = None
        self.current_node_item_name = None
        self.current_node_item_type = None

        self.zoom_in_factor = 1.25
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = (0, 8)
        self.zoom_clamp = True

        self.init_ui()

    def init_ui(self):
        self.setScene(self.gr_scene)
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
        # custom right menu
        self.setContextMenuPolicy(Qt.DefaultContextMenu)

    # ------------------MODE--------------------

    def set_select_mode(self):
        self.mode = MOUSE_SELECT
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCursor(Qt.ArrowCursor)
        debug("Now is <select> mode")

    def set_movable_mode(self):
        self.mode = MOUSE_MOVE
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        debug("Now is <move> mode")

    def set_editing_mode(self, node_name, node_type):
        self.mode = MOUSE_EDIT
        self.current_node_item_name = node_name
        self.current_node_item_type = node_type
        self.set_edit_node_cursor()
        self.status_bar_msg(f'Select: {node_name} item in {node_type}.')
        debug("Now is <edit> mode")

    def set_delete_mode(self):
        self.mode = NODE_DELETE
        del_icon = QPixmap(icon['TRASH']).scaled(32, 32)
        self.setCursor(QCursor(del_icon))
        debug("Now is <delete> mode")

    def set_edge_direct_mode(self):
        self.mode = NODE_CONNECT
        self.edge_type = EDGE_DIRECT
        self.setCursor(Qt.CrossCursor)
        debug("Now is <connect-direct> mode")

    def set_edge_curve_mode(self):
        self.mode = NODE_CONNECT
        self.edge_type = EDGE_CURVES
        self.setCursor(Qt.CrossCursor)
        debug("Now is <connect-curve> mode")

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
        if self.mode == EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.drag_edge.gr_edge.set_dst(pos.x(), pos.y())
            self.drag_edge.gr_edge.update()

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

        # set the gr_scene scale
        if not clamped or self.zoom_clamp is False:
            self.scale(zoom_factor, zoom_factor)

    def keyPressEvent(self, event):
        """
        key V: select
        key M: move
        key D: direct
        key C: curve
        """
        if event.key() == Qt.Key_V:
            self.set_select_mode()
        elif event.key() == Qt.Key_M:
            self.set_movable_mode()
        elif event.key() == Qt.Key_D:
            self.set_edge_direct_mode()
        elif event.key() == Qt.Key_C:
            self.set_edge_curve_mode()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        # get the item that right clicked on
        item = self.get_item_at_click(event)
        if isinstance(item, KMBNodeGraphicItem):
            self.pop_up_right_menu.emit(item.id_str)
            # get item self right menu to display
            item.contextMenuEvent(event)

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
        item = self.get_item_at_click(event)
        if self.mode == MOUSE_EDIT:
            self.add_selected_node_item()

        elif self.mode == NODE_DELETE:
            self.del_selected_node_item(item)

        elif self.mode == NODE_CONNECT:
            if item is not None:
                self.mode = EDGE_DRAG
                self.edge_drag_start(item)

        else:
            self.set_selected_node_item(item)

            if hasattr(item, 'node') or item is None or isinstance(item, KMBGraphicEdgeDirect):
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
        if self.mode == EDGE_DRAG:
            self.mode = NODE_CONNECT
            if item is not None and\
               item is not self.drag_start_item and\
               not issubclass(item.__class__, KMBGraphicEdge):
                self.edge_drag_end(item, event)
            else:
                # if it's nothing then drop this edge
                debug(f"[dropped] => {self.drag_edge} cause nothing happened.")
                self.drag_edge.remove()
                self.drag_edge = None

        else:
            if hasattr(item, "node") or item is None or isinstance(item, KMBGraphicEdgeDirect):
                if event.modifiers() & Qt.ShiftModifier:
                    event.ignore()
                    fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                             Qt.LeftButton, Qt.NoButton,
                                             event.modifiers() | Qt.ControlModifier)
                    super().mouseReleaseEvent(fake_event)
                    return
            super().mouseReleaseEvent(event)

    def right_mouse_button_pressed(self, event):
        # it will cancel all the mode and back to select mode.
        if self.mode == EDGE_DRAG:
            self.drag_edge.remove()
            self.drag_edge = None
        self.set_select_mode()

    def right_mouse_button_released(self, event):
        # self.set_select_mode()
        pass

    # ------------------UTILS--------------------

    def get_item_at_click(self, event):
        """ Return the object that clicked on. """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def add_selected_node_item(self):
        # add new node
        x, y = int(self.last_scene_mouse_pos.x()),\
               int(self.last_scene_mouse_pos.y())
        node = KMBNodeItem(self.gr_scene,
                           self.current_node_item_name,
                           self.current_node_item_type)
        # add into scene and get count of nodes.
        self.gr_scene.scene.add_node(node)
        count = self.gr_scene.scene.get_node_count(node)
        self.add_new_node_item.emit(node.gr_name,
                                    node.gr_type,
                                    node.gr_node.id_str,
                                    count)
        self.status_bar_msg(f'Add: {self.current_node_item_name} node.')
        node.set_pos(x, y)

    def set_selected_node_item(self, item):
        # get args of node and edit it
        if item is not None and isinstance(item, KMBNodeGraphicItem):
            # if select obj, send its name.
            self.selected_node_item.emit(item.id_str)
            self.status_bar_msg(f'Select: {item.name} node.')
        else:
            # if select no obj, send empty signal to clear arg panel.
            self.selected_node_item.emit('null')

    def del_selected_node_item(self, item):
        # del selected node
        if item is not None:
            if isinstance(item, KMBNodeGraphicItem):
                self.selected_delete_node.emit(item.id_str)
                # after deleting stored model, then node graphic.
                self.status_bar_msg(f'Delete: {item.name} node.')
                self.gr_scene.removeItem(item)
                self.gr_scene.scene.remove_node(item.node)
            elif issubclass(item.__class__, KMBGraphicEdge):
                self.status_bar_msg("Delete: one edge.")
                self.gr_scene.removeItem(item)
                self.gr_scene.scene.remove_edge(item.edge)

    def set_edit_node_cursor(self):
        pix = QPixmap(icon['CROSS']).scaled(30, 30)
        self.setCursor(QCursor(pix))

    def set_chosen_state_from_rm(self, _):
        # if not choose one arg item from menu,
        # then del this edge, and this is sign.
        self.has_chosen_from_rm = True

    def edge_drag_start(self, item):
        # pass the wrapper of gr_scene and gr_node
        self.drag_start_item = item
        self.has_chosen_from_rm = False
        self.drag_edge = KMBEdge(self.gr_scene.scene,
                                 item.node,
                                 None, self.edge_type)
        debug(f"[start dragging edge] => {self.drag_edge} at {item}")

    def edge_drag_end(self, item, event):
        debug(f"[stop dragging edge] => {self.drag_edge} at {item}")
        new_edge = KMBEdge(self.gr_scene.scene,
                           self.drag_start_item.node,
                           item.node,
                           self.edge_type)
        # remove the dragging dash edge.
        self.drag_edge.remove()
        self.drag_edge = None
        # saving for the new edge.
        saving_state = new_edge.store()
        # -1 (Invalid), 0 (Valid but not display), 1 (Valid and display)
        if saving_state == -1:  # fail to add new edge.
            self.gr_scene.removeItem(new_edge.gr_edge)
            debug("[dropped] invalid connection.")
        else:  # add new edge successfully.
            debug(f"[connect] {self.drag_start_item} ~ {item} => {new_edge}")
            # only ref edge is able to pop up right menu of the end item,
            # so now you're able to pick up which arg it ref to.
            if self.edge_type == EDGE_CURVES:
                self.contextMenuEvent(event)
            # if hadn't chosen a item in right menu,
            # then give up this edge.
            if not self.has_chosen_from_rm:
                self.del_selected_node_item(new_edge.gr_edge)
            # just remove gr-edge this time.
            if saving_state == 0:
                self.gr_scene.removeItem(new_edge.gr_edge)
                debug(f"[dropped] repeating edge but stored.")
