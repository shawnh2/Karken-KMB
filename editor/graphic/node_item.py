from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsPixmapItem,
                             QMenu, QAction, QInputDialog)
from PyQt5.QtGui import QPixmap, QCursor, QIcon

from editor.graphic.node_text import KMBNodeTextItem
from lib import debug, write_custom_pin, update_custom_pin
from cfg import NODE_ICONx85_PATH, icon


class KMBNodeGraphicItem(QGraphicsPixmapItem):

    def __init__(self, node, name, sort, main_editor, parent=None):
        super().__init__(parent)
        self.node = node  # the wrapper of itself
        self.name = name
        self.sort = sort
        self.main_editor = main_editor
        self.pix = QPixmap(NODE_ICONx85_PATH.format(self.sort, self.name))
        self.current_pos = None
        self.text = KMBNodeTextItem(self.name, self)

        self.width = 85
        self.height = 85
        self.id_str = str(id(self))

        self.right_menu = QMenu()
        self.rm_pin = QIcon(icon['PIN_RM'])
        self.rm_pin_up = QIcon(icon['PIN_UPDATE'])

        self.rm_token = QIcon(icon['TOKEN'])
        self.rm_free = QIcon(icon['FREE'])
        self._ref_item = None

        self.rm_input = QIcon(icon['INPUTS'])
        self.rm_output = QIcon(icon['OUTPUTS'])
        self._io_item = None
        self._edge_id = None

        self.setPixmap(self.pix)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)

    def __repr__(self):
        return f"<NodeGrItem {self.name} {id(self)}>"

    def set_pos(self, x, y):
        dis = self.width / 2
        self.setPos(x - dis, y - dis)

    def is_modified(self):
        # send self modified state.
        self.main_editor.send_modify_state_to_main()

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
        self.is_modified()
        # update selected node and its edge
        for node in self.scene().scene.nodes.values():
            if node.gr_node.isSelected():
                node.update_connect_edges()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        self.text.appear()

    def hoverLeaveEvent(self, event):
        self.text.disappear()

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

    # ------------OPERATIONS ON RIGHT MENU--------------

    def get_context_menu(self):
        """
        Right menu all has three different contents:
        1.For Layer node, right menu shows items that can be referenced.

        2.For PlaceHolder or Units (etc.), menu shows items that already
        has been referenced.

        3.For Model, menu shows inputs and outputs items.
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
        # only Units can be pined.
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
                    action.setIcon(self.rm_input)
                    inputs.append(action)
                else:
                    action.setIcon(self.rm_output)
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
        # about pin actions.
        actions = []
        # actions about pined node itself.
        if self.node.pin_id is not None:
            update = QAction(self.rm_pin_up, 'Update pin')
            update.triggered.connect(self._exec_update_pin_action)
            actions.append(update)
        # for those who are not be pined.
        else:
            pin = QAction(self.rm_pin, 'Add to pins')
            pin.triggered.connect(self._exec_add_pin_action)
            actions.append(pin)
        return actions

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

        def action_layer_type_check() -> bool:
            """
            TimeDistributed and Bidirectional are able to
            have ref edges, but only available for arg `layer`.
            """
            if arg_name == 'layer':
                return True
            return False

        arg_name, idx = args
        support_type = self._ref_item.gr_sort.lower()
        # if ref src is Units, then only few arg item can add ref.
        # or get the layer node that can accept other layer as its arg.
        # so here do some simple check.
        if self._ref_item.gr_type == 'Units':
            if not action_units_type_check():
                action.setDisabled(True)
        elif self.name in ("TimeDistributed", "Bidirectional") and\
             self._ref_item.gr_type == 'Layers':
            if not action_layer_type_check():
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

    # ------------OPERATIONS ON PINS--------------

    def _popup_input_dialog(self):
        # get pin item custom name before save.
        name, ok = QInputDialog.getText(self.main_editor, "Please input Pin Node name",
                                        "This node will be added in Pins with its arguments.")
        return name if ok else False

    # TODO: node after adding in pins.

    def _exec_add_pin_action(self):
        """ Execute Pin action here. Add item to Pin panel. """
        pin_name = self._popup_input_dialog()
        # give up this operation if got cancel.
        if not pin_name:
            debug('[PIN] canceled.')
            return
        debug(f'[PIN] item => {pin_name}')
        # pin only save its changed args not referenced.
        write_custom_pin(pin_name, *self._arg_model.extract_pin())

    def _exec_update_pin_action(self):
        """ Execute update pin action by its pin_id. """
        update_custom_pin(self.node.pin_id,
                          self._arg_model.extract_pin()[0])
        debug(f'[PIN] item update successfully.')
