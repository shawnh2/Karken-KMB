from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QMenu, QAction
from PyQt5.QtGui import QPixmap, QCursor, QIcon

from cfg import NODE_ICONx85_PATH, icon


class KMBNodeGraphicItem(QGraphicsPixmapItem):

    def __init__(self, node, name, parent=None):
        super().__init__(parent)
        self.node = node  # the wrapper of itself
        self.name = name
        self.pix = QPixmap(NODE_ICONx85_PATH.format(self.name))
        self.current_pos = None

        self.width = 85
        self.height = 85
        self.id_str = str(id(self))

        self.right_menu = QMenu()
        self.rm_token = QIcon(icon['TOKEN'])
        self.rm_free = QIcon(icon['FREE'])
        self._ref_item = None

        self.setPixmap(self.pix)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def __str__(self):
        return f"<NodeGrItem {hex(id(self))}>"

    def __repr__(self):
        return f"<NodeGrItem {hex(id(self))}>"

    def set_pos(self, x, y):
        dis = self.width / 2
        self.setPos(x - dis, y - dis)

    def feed_args(self, dst_model):
        self._arg_model = dst_model

    def feed_ref(self, ref_item):
        # the ref edge (wrapper): start item
        self._ref_item = ref_item

    def clean_ref(self):
        self._ref_item = None

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # update selected node and its edge
        for node in self.scene().scene.nodes:
            if node.gr_node.isSelected():
                node.update_connect_edges()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def get_context_menu(self):
        inh_actions = []  # actions for inherit args
        org_actions = []  # actions for original args
        for idx, arg_name, arg_value in self._arg_model.items():
            if arg_value.dtype == 'Reference':
                # set different state mark
                if arg_value.is_referenced:
                    action = QAction(self.rm_token,
                                     arg_name.text() + ' ~ ' + arg_value.get_var_name())
                    action.setDisabled(True)
                else:
                    action = QAction(self.rm_free, arg_name.text())
                # only after dragging ref curve to an item,
                # will get attribute: '_ref_item', so setup some signals.
                if self._ref_item is not None:
                    # set its id and the idx of this arg, also src id.
                    action.setObjectName(f'{self.id_str}-{idx}-{self._ref_item.gr_node.id_str}')
                    action.triggered.connect(self.node.gr_scene.right_menu_listener)
                # collect action
                if idx <= self._arg_model.io_separator:
                    inh_actions.append(action)
                else:
                    org_actions.append(action)
        return inh_actions, org_actions

    def contextMenuEvent(self, event):
        if self._ref_item is not None:
            # it means this right menu is called after ref edge.
            # add custom sign at head
            sign = QAction(f'{self._ref_item.gr_name}-')
        else:
            sign = QAction('Reference Table')
        sign.setEnabled(False)
        self.right_menu.addAction(sign)
        self.right_menu.addSeparator()
        # getting the args of its own and
        # highlight the Reference (suggested) one.
        inh_actions, org_actions = self.get_context_menu()
        self.right_menu.addActions(inh_actions)
        self.right_menu.addSeparator()
        self.right_menu.addActions(org_actions)
        # show right menu
        self.right_menu.exec(QCursor.pos())
        # clean ref after using
        self.clean_ref()
