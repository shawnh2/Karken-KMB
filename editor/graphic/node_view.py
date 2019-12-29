from PyQt5.QtWidgets import QGraphicsView, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QMouseEvent, QCursor, QPixmap, QWheelEvent

from editor.graphic.node_item import KMBNodeGraphicItem
from editor.graphic.node_edge import KMBGraphicEdge
from editor.graphic.node_note import KMBNote
from editor.wrapper.wrap_item import KMBNodeItem
from editor.wrapper.wrap_edge import KMBEdge
from editor.component.edge_type import KMBGraphicEdgeBezier, KMBGraphicEdgeDirect
from editor.component.messages import PopMessageBox
from editor.widgets.sidebar import KMBViewSideBar
from editor.threads import OrganizingThread, SearchBarThread

from cfg import icon, EDGE_CURVES, EDGE_DIRECT
from lib import debug


MOUSE_SELECT = 0
MOUSE_MOVE = 1
MOUSE_EDIT = 2
MOUSE_NOTE = 3

NODE_SELECTED = 4
NODE_DELETE = 5
NODE_CONNECT = 6

EDGE_DRAG = 7


class KMBNodeGraphicView(QGraphicsView):

    # ------------------SIGNALS--------------------

    # show the changing position in status bar.
    SCENE_POS_CHANGED = pyqtSignal(int, int)            # x, y coord

    # send to node args for creating a new args model for this node.
    # name, type, id, count, pin_args ('None' means empty)
    ADD_NEW_NODE_ITEM = pyqtSignal(str, str, str, int, str)

    # pass the id of selected node item to node args for editing.
    SELECTED_NODE_ITEM = pyqtSignal(str)                # id or state

    # send to node args for deleting its args model.
    SELECTED_DELETE_NODE = pyqtSignal(str)              # id

    # pop up the right menu of clicked node,
    # also emit the src node id along with.
    POP_UP_RIGHT_MENU = pyqtSignal(str)                 # dst id

    # del ref related items if one ref edge got deleted.
    DEL_REF_RELATED_ITEMS = pyqtSignal(str, str)        # referenced src id, dst id
    DEL_IO_EDGE_ITEM = pyqtSignal(str, str)             # io src id, dst id

    # whether current project has been modified.
    IS_MODIFIED = pyqtSignal(bool)

    # ------------------INIT--------------------

    def __init__(self,
                 graphic_scene,
                 status_bar_msg,
                 parent=None):
        super().__init__(parent)

        self.gr_scene = graphic_scene
        self.status_bar_msg = status_bar_msg
        self.sidebar = KMBViewSideBar(self)
        self.search_bar = SearchBarThread(self)
        self.parent = parent
        self.del_items_msg = PopMessageBox('Delete items', self)

        self.mode = MOUSE_SELECT
        self.edge_type = None
        # signals from sidebar.
        self.disable_wheel = False
        self.has_pressed_zoom_btn = False
        # signals from right menu.
        self.has_chosen_from_rm = False
        self.has_chosen_to_del_from_rm = False
        # signals from note.
        self.has_finished_editing = True

        # current dynamic variables.
        self.last_scene_mouse_pos = None
        self.current_node_item_name = None
        self.current_node_item_type = None
        self.current_node_item_sort = None
        # optional
        self.current_node_pin_args = None
        self.current_node_pin_id = None
        # record group selected items.
        self.rubber_select = []

        self.zoom_in_factor = 1.25
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = (0, 8)
        self.zoom_clamp = True

        self.init_ui()
        self.init_slots()

    def init_ui(self):
        self.setScene(self.gr_scene)
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.HighQualityAntialiasing |
                            QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform |
                            QPainter.LosslessImageRendering)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        # default drag mode
        self.setDragMode(self.RubberBandDrag)
        # custom right menu
        self.setContextMenuPolicy(Qt.DefaultContextMenu)

    def init_slots(self):
        # init slots from sidebar.
        self.sidebar.LOCK_WHEEL.connect(self.set_wheel_disable)
        self.sidebar.ZOOM_IN.connect(self.set_one_zoom_in)
        self.sidebar.ZOOM_OUT.connect(self.set_one_zoom_out)
        self.sidebar.NODE_ORGANIZE.connect(self.organize_nodes)
        self.sidebar.NODE_LOCATE.connect(self.locating_center)

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

    def set_editing_mode(self, *args):
        self.mode = MOUSE_EDIT
        if len(args) == 3:  # ... normal case
            node_name, node_type, node_sort = args
            self.status_bar_msg(f'Select: {node_name} item in '
                                f'{node_type}:{node_sort}.')
        else:  # ...from pin box
            (node_name, node_type, node_sort,
             pin_args, pin_id) = args
            self.current_node_pin_args = pin_args
            self.current_node_pin_id = pin_id
            self.status_bar_msg(f'Select: {node_name} item in Pins.')
        self.current_node_item_name = node_name
        self.current_node_item_type = node_type
        self.current_node_item_sort = node_sort
        self.set_edit_node_cursor()
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

    def set_note_mode(self):
        self.mode = MOUSE_NOTE
        self.has_finished_editing = False
        self.setCursor(Qt.IBeamCursor)
        debug("Now is <note> mode")

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
        pos = event.pos()
        if self.mode == EDGE_DRAG:
            sc_pos = self.mapToScene(pos)
            self.drag_edge.gr_edge.set_dst(sc_pos.x(), sc_pos.y())
            self.drag_edge.gr_edge.update()

        # emit pos changed signal
        self.last_scene_mouse_pos = self.mapToScene(pos)
        self.SCENE_POS_CHANGED.emit(
            int(self.last_scene_mouse_pos.x()),
            int(self.last_scene_mouse_pos.y())
        )
        # enter the hot area of sidebar.
        if (
            self.sidebar.x + self.sidebar.w >= pos.x() >= self.sidebar.x and
            self.sidebar.y + self.sidebar.h >= pos.y() >= self.sidebar.y + self.sidebar.margin_bottom
        ):
            if not self.sidebar.on_display:
                self.sidebar.slide_in_animation()
        else:
            if self.sidebar.on_display:
                self.sidebar.slide_out_animation()

        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        # check whether should be end.
        if self.disable_wheel:
            if self.has_pressed_zoom_btn:
                self.has_pressed_zoom_btn = False
            else:
                return

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
        """ Shortcut: available only view is focused.
        key V - select
        key H - move
        key D - direct edge
        key R - curve edge
        key T - note
        """
        if self.mode == MOUSE_NOTE or not self.has_finished_editing:
            if event.key() == Qt.Key_Escape:
                self.set_select_mode()
        else:
            if event.key() == Qt.Key_V:
                self.set_select_mode()
            elif event.key() == Qt.Key_H:
                self.set_movable_mode()
            elif event.key() == Qt.Key_D:
                self.set_edge_direct_mode()
            elif event.key() == Qt.Key_R:
                self.set_edge_curve_mode()
            elif event.key() == Qt.Key_T:
                self.set_note_mode()
            elif event.key() == Qt.Key_Escape:
                # it can bring back the search bar.
                if self.search_bar.is_display():
                    self.search_bar(self.search_bar.cb_slide_out)
        super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        # get the item that right clicked on
        item = self.get_item_at_click(event)
        if isinstance(item, KMBNodeGraphicItem):
            self.POP_UP_RIGHT_MENU.emit(item.id_str)
            # get item self right menu to display
            item.contextMenuEvent(event)

    def resizeEvent(self, event):
        w = event.size().width()
        h = event.size().height()
        self.sidebar.update_pos(w, h)
        self.search_bar((self.search_bar.cb_set_size, w, h))

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
            self.add_node()

        elif self.mode == MOUSE_NOTE:
            if isinstance(item, KMBNote):
                # edit the existing note item.
                item.into_editor()
            else:
                self.add_note()

        elif self.mode == NODE_DELETE:
            # delete group
            if self.rubber_select:
                self.del_items_msg.make('Sure to delete all selected items?',
                                        PopMessageBox.TYPE_YES_OR_NO)
                res = self.del_items_msg.exec()
                if res == QMessageBox.Yes:
                    self.del_selected_items()
            # delete single
            else:
                self.del_selected_item(item)

        elif self.mode == NODE_CONNECT:
            if item is not None and isinstance(item, KMBNodeGraphicItem):
                self.mode = EDGE_DRAG
                self.edge_drag_start(item)

        else:
            self.set_node(item)

            if hasattr(item, 'node') or item is None or issubclass(item.__class__, KMBGraphicEdge):
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
            if (
                isinstance(item, KMBNodeGraphicItem) and
                item is not self.drag_start_item
            ):
                self.edge_drag_end(item, event)
            else:
                # if it's nothing then drop this edge
                debug(f"[dropped] => {self.drag_edge} cause nothing happened.")
                self.drag_edge.remove()
                self.drag_edge = None

        elif self.mode == MOUSE_SELECT:
            # record the group selected result,
            # if it's None, then will get a empty list.
            self.get_items_at_rubber()
            super().mouseReleaseEvent(event)

        else:
            if hasattr(item, "node") or item is None or issubclass(item.__class__, KMBGraphicEdge):
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

    # ------------------OPERATIONS--------------------

    def add_node(self, *args):
        # add new node, args is feeding from search bar.
        self.is_modified()
        if args:
            self.current_node_item_name = args[0]
            self.current_node_item_sort = args[1]
            self.current_node_item_type = args[2]
            self.current_node_pin_id = None
            self.current_node_pin_args = args[3]
            x, y = args[4]
        else:
            x, y = self.get_last_xy()
        node = KMBNodeItem(self.gr_scene,
                           self.current_node_item_name,
                           self.current_node_item_type,
                           self.current_node_item_sort,
                           self.current_node_pin_id,
                           self.parent)
        node.set_pos(x, y)
        # add into scene and get count of nodes.
        self.gr_scene.scene.add_node(node)
        count = self.gr_scene.scene.get_node_count(node.gr_name)
        self.ADD_NEW_NODE_ITEM.emit(self.current_node_item_name,
                                    self.current_node_item_type,
                                    node.gr_node.id_str,
                                    count, str(self.current_node_pin_args))
        self.status_bar_msg(f'Add: {self.current_node_item_name} node.')
        self.drop_received_pin()

    def add_note(self):
        # add note in scene.
        x, y = self.get_last_xy()
        note = KMBNote(self.gr_scene, x, y)
        note.FINISHED_EDITING.connect(self.set_finished_editing)
        self.set_select_mode()

    def set_node(self, item):
        # get args of node and edit it
        if item is not None and isinstance(item, KMBNodeGraphicItem):
            # if select obj, send its name.
            self.SELECTED_NODE_ITEM.emit(item.id_str)
            self.status_bar_msg(f'Select: {item.name} node.')
        else:
            # if select no obj, send empty signal to clear arg panel.
            self.SELECTED_NODE_ITEM.emit('null')

    def del_selected_item(self, item):
        # del selected node or edge
        if item is not None:
            self.is_modified()
            if isinstance(item, KMBNodeGraphicItem):
                self._del_node_item(item)
            elif issubclass(item.__class__, KMBGraphicEdge):
                self._del_edge_item(item)
            elif isinstance(item, KMBNote):
                self._del_note_item(item)

    def del_selected_items(self):
        self.is_modified()
        # del the selected items
        for item in self.rubber_select:
            self.del_selected_item(item)
        self.rubber_select.clear()

    def _del_node_item(self, node):
        self.SELECTED_DELETE_NODE.emit(node.id_str)
        # del the stored model.
        self.status_bar_msg(f'Delete: {node.name} node.')
        self.gr_scene.scene.remove_node(node.node)
        # del the node in view.
        self.gr_scene.removeItem(node)

    def _del_edge_item(self, edge):
        # del direct edge directly.
        self.status_bar_msg('Delete: One edge.')
        if isinstance(edge, KMBGraphicEdgeBezier):
            self.has_chosen_to_del_from_rm = False
            # curve edge need to del the ref.
            src_item_id = str(id(edge.edge.start_item.gr_node))
            dst_item_id = str(id(edge.edge.end_item.gr_node))
            self.DEL_REF_RELATED_ITEMS.emit(src_item_id, dst_item_id)

            if not self.has_chosen_to_del_from_rm:
                return

        elif isinstance(edge, KMBGraphicEdgeDirect):
            # only works if edge's end is Model.
            if edge.edge.end_item.gr_name == 'Model':
                src_item_id = str(id(edge.edge.start_item.gr_node))
                dst_item_id = str(id(edge.edge.end_item.gr_node))
                self.DEL_IO_EDGE_ITEM.emit(src_item_id, dst_item_id)
            self.gr_scene.removeItem(edge)
        # remove edge from view and history.
        self.gr_scene.scene.remove_edge(edge.edge)
        self.gr_scene.removeItem(edge)

    def _del_note_item(self, note):
        self.gr_scene.scene.remove_note(note)
        self.gr_scene.removeItem(note)

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
        # -1 (Invalid), 1 (Valid and display)
        if saving_state == -1:  # fail to add new edge.
            self.gr_scene.removeItem(new_edge.gr_edge)
            debug("[dropped] invalid connection.")
        else:  # add new edge successfully.
            debug(f"[connect] {self.drag_start_item} ~ {item} => {new_edge}")
            # only ref edge is able to pop up right menu of the end item,
            # so now you're able to pick up which arg it ref to.
            if self.edge_type == EDGE_CURVES:
                self._curve_edge_drag_end(event, new_edge)
            # for Model, show its input and output in right menu.
            if self.edge_type == EDGE_DIRECT:
                self._direct_edge_drag_end(event, item, new_edge)

    def _curve_edge_drag_end(self, event, new_edge):
        """ Event while end up dragging curve edge. """
        self.contextMenuEvent(event)
        # if hadn't chosen a item in right menu,
        # then give up this edge.
        if not self.has_chosen_from_rm:
            self.gr_scene.removeItem(new_edge.gr_edge)
            self.has_chosen_from_rm = False
            self.gr_scene.scene.history.destroy_edge(new_edge)
            debug("[dropped] triggered no item in right menu.")
        else:
            self.is_modified()

    def _direct_edge_drag_end(self, event, item, new_edge):
        """ Event while end up dragging direct edge.
        This method is specially for <Model> node. """
        # display its inputs and outputs in right menu.
        if item.name == 'Model':
            self.contextMenuEvent(event)
            if not self.has_chosen_from_rm:
                self.gr_scene.removeItem(new_edge.gr_edge)
                self.gr_scene.scene.history.destroy_edge(new_edge)
                debug("[dropped] triggered no item in right menu.")
            else:
                self.is_modified()
        else:
            self.is_modified()

    # ------------------UTILS--------------------

    def drop_received_pin(self):
        """ Drop all the received pin value after using. """
        self.current_node_pin_id = None
        self.current_node_pin_args = None

    def bring_search_bar(self):
        if self.search_bar.is_display():
            self.search_bar(self.search_bar.cb_slide_out)
        else:
            self.search_bar(self.search_bar.cb_slide_in)

    def get_item_at_click(self, event):
        """ Return the object that clicked on. """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def get_items_at_rubber(self):
        """ Get group select items. """
        area = self.rubberBandRect()
        self.rubber_select = self.items(area)

    def get_last_xy(self):
        # return the last position of mouse in scene.
        return int(self.last_scene_mouse_pos.x()), int(self.last_scene_mouse_pos.y())

    def set_edit_node_cursor(self):
        pix = QPixmap(icon['CROSS']).scaled(30, 30)
        self.setCursor(QCursor(pix))

    def is_modified(self):
        # if current project has any changes,
        # including args then will trigger this.
        self.IS_MODIFIED.emit(True)

    def set_chosen_item_from_rm(self, _):
        # if not choose one arg item from menu to ref/io,
        # then del this edge, and this is sign.
        self.has_chosen_from_rm = True

    def set_chosen_to_del_from_rm(self, _):
        # if not choose one arg item from menu to del,
        # then give up this operation.
        self.has_chosen_to_del_from_rm = True

    def set_wheel_disable(self, state: bool):
        # on Mac: touch pad may have bad exp if wheel is enable.
        self.disable_wheel = state

    def set_finished_editing(self, state: bool):
        # note has finished editing.
        self.has_finished_editing = state

    def set_one_zoom_in(self):
        # zoom in once.
        fake_wheel_event = QWheelEvent(
            QPoint(0, 0),      # pos(fake)
            QPoint(0, 0),      # global-pos(fake)
            QPoint(0, 2),      # pixel-delta(fake)
            QPoint(0, 120),    # angle-delta(fake)
            0,                 # phase
            Qt.Vertical,       # orientation
            Qt.LeftButton,     # button
            Qt.KeyboardModifierMask  # keyboard
        )
        # enable wheel, disable it after using.
        self.has_pressed_zoom_btn = True
        # feed it to wheel.
        self.wheelEvent(fake_wheel_event)

    def set_one_zoom_out(self):
        # zoom out once.
        fake_wheel_event = QWheelEvent(
            QPoint(0, 0),
            QPoint(0, 0),
            QPoint(0, -2),
            QPoint(0, -120),
            0,
            Qt.Vertical,
            Qt.LeftButton,
            Qt.KeyboardModifierMask
        )
        self.has_pressed_zoom_btn = True
        self.wheelEvent(fake_wheel_event)

    def organize_nodes(self):
        # start organizing nodes in another thread.
        OrganizingThread(self.gr_scene.scene.history.nodes)()

    def locating_center(self):
        # locating to view center.
        self.centerOn(0, 0)
        item = self.grab()
        item.save('test/test.png')
