from PyQt5.QtGui import QStandardItemModel

from editor.component.args_model_item import (ArgNameItem, ArgTypeItem,
                                              ArgEditItem, ArgMarkItem)


class ArgsSuperModel(QStandardItemModel):

    def __init__(self,
                 db_link,
                 node_name: str,
                 node_id_string: str,
                 inherit: str):
        super().__init__()

        self.db = db_link
        self.node_name = node_name
        self.id_string = node_id_string
        self.inherit = inherit
        self.n = 0

    def set_header_labels(self, header1: str, header2: str):
        # only two headers available
        self.setHorizontalHeaderLabels((header1, header2))

    def _get_inherit_args(self):
        for i, arg in self.db.get_inh_args(self.inherit):
            self.feed_inherit_item(i, arg)
            # add counter
            self.n += 1

    def _get_original_args(self):
        for i, arg in self.db.get_org_args(self.id_string):
            self.feed_original_item(i + self.n, arg)

    def _get_custom_args(self):
        name = ArgNameItem('var',
                           'The name of this variable.',
                           'var_name')
        value = ArgEditItem("String", self.node_name.lower())
        self.set_col_items(self.n, name, value)
        self.n += 1

    def get_args(self, add_custom_args=False):
        # call this method to get all the args
        if self.inherit:
            self._get_inherit_args()
        if add_custom_args:
            self._get_custom_args()
        if self.id_string:
            self._get_original_args()

    def feed_inherit_item(self, idx, unpack_item):
        raise NotImplementedError

    def feed_original_item(self, idx, unpack_item):
        raise NotImplementedError

    def set_col_items(self, col_idx, *items):
        for i, item in enumerate(items):
            self.setItem(col_idx, i, item)


class ArgsPreviewModel(ArgsSuperModel):

    def __init__(self,
                 db_link,
                 node_name: str,
                 node_id: str,
                 inherit: str):
        super().__init__(db_link, node_name, node_id, inherit)
        # set header labels for this model
        self.set_header_labels("Type", "Argument Name")

    def feed_inherit_item(self, idx, unpack_item):
        # id, name, init, type, info
        _, arg_name, arg_init, arg_type, arg_info = unpack_item
        arg_name_item = ArgNameItem('inh', arg_info, arg_name)
        arg_type_item = ArgTypeItem(arg_type)
        self.set_col_items(idx, arg_type_item, arg_name_item)

    def feed_original_item(self, idx, unpack_item):
        # id, note, name, init, type, info, box
        _, _, arg_name, arg_init, arg_type, arg_info, arg_box = unpack_item
        arg_name_item = ArgNameItem('org', arg_info, arg_name)
        arg_type_item = ArgTypeItem(arg_type)
        self.set_col_items(idx, arg_type_item, arg_name_item)


class ArgsEditableModel(ArgsSuperModel):

    def __init__(self,
                 db_link,
                 node_name: str,
                 node_id: str,
                 inherit: str):
        super().__init__(db_link, node_name, node_id, inherit)
        # args: combobox style cell
        self.combo_args = []
        self.combo_widgets_id = []
        # args: check button style cell
        self.check_args = []
        self.check_widgets_id = []
        # where store the name of this node
        self.name = ""
        # set header labels for this model
        self.set_header_labels("Name", "Argument Value")

    def reassign_value(self, idx, value: str):
        self.combo_args[idx][4] = value
        self.combo_args[idx][5] = True

    def reassign_state(self, idx, state: str):
        self.check_args[idx][2] = state
        self.check_args[idx][3] = ~self.check_args[idx][3]  # reverse the has-changed sign

    def feed_inherit_item(self, idx, unpack_item):
        # id, name, init, type, info
        _, arg_name, arg_init, arg_type, arg_info = unpack_item
        arg_type_item = ArgTypeItem(arg_type)
        arg_name_item = ArgNameItem('inh', arg_info, arg_name)
        if arg_type == "bool":
            arg_mark_item = ArgMarkItem(1)  # tag: 1 is for check box
            self.check_args.append([idx, 1, arg_init, False])
            self.set_col_items(idx, arg_name_item, arg_mark_item)
        else:
            arg_init_item = ArgEditItem(arg_type_item.raw_type_name, arg_init)
            self.set_col_items(idx, arg_name_item, arg_init_item)

    def feed_original_item(self, idx, unpack_item):
        # id, note, name, init, type, info, box
        _, _, arg_name, arg_init, arg_type, arg_info, arg_box = unpack_item
        arg_type_item = ArgTypeItem(arg_type)
        arg_name_item = ArgNameItem('org', arg_info, arg_name)
        if arg_box:
            # setup the combo box for box args
            arg_box_list = self.db.get_box_args(int(arg_box)).split(';')
            self.combo_args.append([idx, 1, arg_init, arg_box_list, "placeholder", False])
            # placeholder is where to store the current value
            arg_mark_item = ArgMarkItem(2)  # tag: 2 is for combo box
            self.set_col_items(idx, arg_name_item, arg_mark_item)
        elif arg_type == "bool":
            # setup the check button for bool type
            arg_mark_item = ArgMarkItem(1)  # tag: 1 is for check box
            self.check_args.append([idx, 1, arg_init, False])
            self.set_col_items(idx, arg_name_item, arg_mark_item)
        else:
            arg_init_item = ArgEditItem(arg_type_item.raw_type_name, arg_init)
            self.set_col_items(idx, arg_name_item, arg_init_item)
