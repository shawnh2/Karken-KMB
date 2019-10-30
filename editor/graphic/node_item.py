from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QMenu, QAction
from PyQt5.QtGui import QPixmap, QCursor, QIcon

from cfg import NODE_ICONx85_PATH, icon


class KMBNodeGraphicItem(QGraphicsPixmapItem):

    def __init__(self, node, name, sort, parent=None):
        super().__init__(parent)
        self.node = node  # the wrapper of itself
        self.name = name
        self.sort = sort
        self.pix = QPixmap(NODE_ICONx85_PATH.format(self.sort, self.name))
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

    def contextMenuEvent(self, event):
        # make a menu main header.
        if self._ref_item is not None:
            # it means this right menu is called after ref edge.
            # add custom sign at head.
            sign = QAction(f'Create reference ~ {self._ref_item.gr_name}')
        else:
            sign = QAction(f'Reference Table of <{self._arg_model.var_name}>')
        sign.setEnabled(False)
        self.right_menu.addAction(sign)
        self.right_menu.addSeparator()
        # then add arg item.
        actions_list = self.get_context_menu()
        for actions in actions_list:
            self.right_menu.addActions(actions)
            self.right_menu.addSeparator()
        # show right menu.
        self.right_menu.exec(QCursor.pos())
        # clean ref after using.
        self.clean_ref()

    # TODO: add var-name annotations around item.

    # ------------OPERATIONS ON RIGHT MENU--------------

    def get_context_menu(self):
        """ For Layer node, right menu shows items that can be referenced.
        But for PlaceHolder or Units (etc.), menu shows items that already
        has been referenced.
        """
        if self._arg_model.node_type == 'Layers':
            return self._get_reference_table()
        else:
            return self._get_referenced_table()

    def _get_reference_table(self):
        # for Layer node.
        inh_actions = []  # actions for inherit args
        org_actions = []  # actions for original args
        for idx, arg_name, arg_value in self._arg_model.items():
            if self._conditions(arg_value.dtype):
                action = self._make_a_valid_action(arg_value, arg_name)
                # only after dragging ref curve to a node
                # will get attribute: '_ref_item'.
                if self._ref_item is not None:
                    self._pre_activate_action(action,
                                              arg_name.text(),
                                              idx)
                # collect actions
                if idx <= self._arg_model.io_separator:
                    inh_actions.append(action)
                else:
                    org_actions.append(action)
        return inh_actions, org_actions

    def _get_referenced_table(self):
        # for PlaceHolder, Units and so on.
        actions_list = []
        if self._arg_model.ref_by:
            for node_id, items in self._arg_model.ref_by.items():
                var_name = self._arg_model.rb_semaphore.get_var_name(node_id)
                sub_header = [self._make_a_sub_header(f'{var_name}')]
                actions = [QAction(self.rm_token,
                                   f'   - {item.belong_to}')
                           for item in items.values()]
                actions_list.append(sub_header + actions)
        return actions_list

    def _conditions(cls, *args) -> bool:
        """
        Only show items that fulfill these conditions
        here for reference table on right menu.

        :return: True
        """
        if args[0] == 'Reference':
            return True
        else:
            return False

    def _make_a_valid_action(self, arg_value, arg_name):
        # make a action with different state mark.
        if arg_value.is_referenced:
            action = QAction(self.rm_token,
                             arg_name.text() + ' ~ ' + arg_value.var_name)
            action.setDisabled(True)
        else:
            action = QAction(self.rm_free, arg_name.text())
        return action

    @classmethod
    def _make_a_sub_header(cls, msg: str):
        """ Use a disabled action to represent header. """
        sub_header = QAction(msg)
        sub_header.setEnabled(False)
        return sub_header

    @classmethod
    def _action_units_type_check(cls, arg: str, support_type: str) -> bool:
        """ Check whether this arg support this type.
        Usually, those args which accept the support_type,
        always contains the support_type.

        eg. activation <=accept Activations.
            bias_initializer <=accept Initializers.

        but always with plural form, so get rid of the 's'.
        """
        if arg.__contains__(support_type[:-2]):
            return True
        return False

    def _pre_activate_action(self, action, *args):
        """
        If one item (also action) is ready to accept ref,
        then must pre-activate that action by setting
        different signals and functions.

        :return: One pre-activated action.
        """
        arg_name, idx = args
        support_type = self._ref_item.gr_sort.lower()
        # if ref src is Units, then only few arg item can add ref.
        # so here do some simple check.
        if self._ref_item.gr_type == 'Units':
            if not self._action_units_type_check(arg_name,
                                                 support_type):
                action.setDisabled(True)
        # set its id and the idx of this arg, also src id.
        # using object name as signal here.
        action.setObjectName(f'{self.id_str}-'
                             f'{idx}-'
                             f'{self._ref_item.gr_node.id_str}')
        action.triggered.connect(self.node.gr_scene.right_menu_listener)
