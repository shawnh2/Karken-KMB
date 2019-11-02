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
        self.pin = QIcon(icon['PIN'])

        self.rm_token = QIcon(icon['TOKEN'])
        self.rm_free = QIcon(icon['FREE'])
        self._ref_item = None

        self.i_icon = QIcon(icon['INPUTS'])
        self.o_icon = QIcon(icon['OUTPUTS'])
        self._io_item = None
        self._edge_id = None

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
        # get ref edge's (wrapper) start item.
        self._ref_item = ref_item

    def feed_io(self, io_item, edge_id):
        self._io_item = io_item
        # the id of edge wrapper.
        self._edge_id = edge_id

    def clean_feed(self):
        self._arg_model = None
        self._ref_item = None
        self._io_item = None
        self._edge_id = None

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # update selected node and its edge
        for node in self.scene().scene.nodes.values():
            if node.gr_node.isSelected():
                node.update_connect_edges()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        # add header title at right menu.
        header = self._make_a_main_header()
        self.right_menu.addAction(header)
        self.right_menu.addSeparator()
        # then add menu items.
        actions_list = self.get_context_menu()
        for actions in actions_list:
            self.right_menu.addActions(actions)
            self.right_menu.addSeparator()
        # show right menu.
        self.right_menu.exec(QCursor.pos())
        # clean all after using.
        self.clean_feed()

    # TODO: add var-name annotations around item.

    # ------------OPERATIONS ON RIGHT MENU--------------

    def get_context_menu(self):
        """
        Right menu all has three different contents:
        For Layer node, right menu shows items that can be referenced.

        For PlaceHolder or Units (etc.), menu shows items that already
        has been referenced.

        For Model, menu shows inputs and outputs items.
        """
        if self._arg_model.node_type == 'Layers':  # case 1
            return self._get_reference_table()
        elif self._arg_model.node_name == 'Model':  # case 3
            return self._get_model_io_table()
        else:  # case 2
            return self._get_referenced_table()

    def _get_reference_table(self):
        # for Layer node. can pin.

        def conditions() -> bool:
            """
            Only show items that fulfill these conditions
            here for reference table on right menu.

            :return: True
            """
            if arg_value.dtype == 'Reference':
                return True
            else:
                return False

        inh_actions = []  # actions for inherit args
        org_actions = []  # actions for original args
        for idx, arg_name, arg_value in self._arg_model.items():
            if conditions():
                # make a action with different state mark.
                if arg_value.is_referenced:
                    action = QAction(self.rm_token,
                                     arg_name.text() + ' ~ ' + arg_value.var_name)
                    action.setDisabled(True)
                else:
                    action = QAction(self.rm_free, arg_name.text())
                # only after dragging ref curve to a node
                # will get attribute: '_ref_item'.
                if self._ref_item is not None:
                    self._pre_activate_ref_action(action,
                                                  arg_name.text(), idx)
                # collect actions
                if idx <= self._arg_model.io_separator:
                    inh_actions.append(action)
                else:
                    org_actions.append(action)
        # add `add to pin` item.
        if self._ref_item is None:
            pin = self._make_a_pin_item()
            return inh_actions, org_actions, pin
        return inh_actions, org_actions

    def _get_referenced_table(self):
        # for PlaceHolder, Units and so on.
        actions_list = []
        if self._arg_model.ref_by:
            for node_id, items in self._arg_model.ref_by.items():
                var_name = self._arg_model.rb_semaphore.get_var_name(node_id)
                # make one block.
                sub_header = [self._make_a_sub_header(f'{var_name}')]
                actions = [QAction(self.rm_token,
                                   f'   - {item.belong_to}')
                           for item in items.values()]
                actions_list.append(sub_header + actions)
        # only Units cam pin.
        if self._arg_model.node_type == 'Units':
            pin = self._make_a_pin_item()
            actions_list.append(pin)
        return actions_list

    def _get_model_io_table(self):
        # especially for Model. cannot pin.
        inputs = []
        outputs = []
        for idx, arg_name, arg_value in self._arg_model.items():
            item_name = arg_name.text()
            # sub header show with INPUTS.
            if item_name == 'model_name':
                sub = self._make_a_sub_header(f'Model Name: {arg_value.value}')
                inputs.append(sub)
            # also show the I/O items.
            if item_name == 'inputs' or item_name == 'outputs':
                action = QAction(item_name.upper())
                # normally after right clicking on Model,
                # it will get all the I/O info.
                # but if it gets an I/O, then popup I/O to choose.
                if self._io_item is not None:
                    self._pre_activate_io_action(action, item_name[0])
                # collect item into different container.
                if item_name == 'inputs':
                    action.setIcon(self.i_icon)
                    inputs.append(action)
                else:
                    action.setIcon(self.o_icon)
                    outputs.append(action)
        # display the I/O items if have.
        if self._arg_model.io:
            i_items, o_items = self._arg_model.io
            for i_item in i_items.values():
                i_action = self._make_a_sub_header(' ' * 6 + i_item.value)
                inputs.append(i_action)
            for o_item in o_items.values():
                o_action = self._make_a_sub_header(' ' * 6 + o_item.value)
                outputs.append(o_action)
        return inputs, outputs

    def _make_a_main_header(self):
        """ The main header of popup right menu. """
        if self._ref_item is not None:
            # it means this right menu is called after ref edge.
            # add custom sign at head.
            sign = QAction(f'Create reference ~ {self._ref_item.gr_name}')
        else:
            if self._arg_model.node_name == 'Model':
                sign = QAction(f'Model I/O Table')
            else:
                sign = QAction(f'Reference Table of <{self._arg_model.var_name}>')
        sign.setEnabled(False)
        return sign

    @classmethod
    def _make_a_sub_header(cls, msg: str):
        """ Use a disabled action to represent header. """
        sub_header = QAction(msg)
        sub_header.setEnabled(False)
        return sub_header

    def _make_a_pin_item(self):
        pin = QAction(self.pin, 'Add to Pins')
        pin.triggered.connect(self._execute_pin_action)
        return [pin]

    def _pre_activate_ref_action(self, action, *args):
        """
        If one item (also action) is ready to accept ref,
        then must pre-activate that action by setting
        different signals and functions.

        :return: One pre-activated action.
        """

        def action_units_type_check() -> bool:
            """
            Check whether this arg support this type.
            Usually, those args which accept the support_type,
            always contains the support_type.

            eg. activation <=accept Activations.
                bias_initializer <=accept Initializers.

            but always with plural form, so get rid of the 's'.
            """
            if arg_name.__contains__(support_type[:-2]):
                return True
            return False

        arg_name, idx = args
        support_type = self._ref_item.gr_sort.lower()
        # if ref src is Units, then only few arg item can add ref.
        # so here do some simple check.
        if self._ref_item.gr_type == 'Units':
            if not action_units_type_check():
                action.setDisabled(True)
        # signal field:
        # TYPE - DST_ID - SRC-ID - ARG_IDX
        action.setObjectName(f'REF-'
                             f'{self.id_str}-'
                             f'{self._ref_item.gr_node.id_str}-'
                             f'{idx}')
        action.triggered.connect(self.node.gr_scene.right_menu_listener)

    def _pre_activate_io_action(self, action, mark):
        """ Pre-activate IO action. """
        # signal field:
        # TYPE - DST_ID - SRC-ID - SIGN - EDGE_ID
        action.setObjectName(f'IO-{self.id_str}'
                             f'-{self._io_item.gr_node.id_str}'
                             f'-{mark}-{self._edge_id}')
        # mark: 'i' is inputs, 'o' is outputs.
        action.triggered.connect(self.node.gr_scene.right_menu_listener)

    def _execute_pin_action(self):
        """ Execute Pin action here. Add item to Pin panel. """
        for idx, arg_name_item, arg_value_item in self._arg_model.items():
            # only save the changed value.
            if arg_value_item.is_changed:
                print(arg_name_item.text(), arg_value_item.value)
