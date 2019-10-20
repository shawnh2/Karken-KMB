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

    def feed_args(self, model):
        self.args_model = model

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # update selected node and its edge
        for node in self.scene().scene.nodes:
            if node.gr_node.isSelected():
                node.update_connect_edges()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        right_menu = QMenu()
        suggested = QIcon(icon['SUGGEST'])
        # add sign at head
        sign = QAction(suggested, 'available')
        sign.setEnabled(False)
        right_menu.addAction(sign)
        right_menu.addSeparator()
        # getting the args of its own and
        # highlight the Reference (suggested) one.
        idx = 0
        actions = []
        while True:
            arg_name = self.args_model.item(idx, 0)
            if arg_name is None:
                break
            arg_value = self.args_model.item(idx, 1)
            if arg_value.dtype == 'Reference':
                actions.append(QAction(suggested, arg_name.text()))
            #actions.append(QAction(arg_name.text()))
            # move on to next
            idx += 1
        right_menu.addActions(actions)
        # show right menu
        right_menu.exec(QCursor.pos())
