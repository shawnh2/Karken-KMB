from PyQt5.QtGui import QStandardItemModel

from editor.component.args_model_item import ArgNameItem, ArgTypeItem, ArgEditItem
from editor.component.semaphores import ReferenceBySemaphore


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
        self.io_separator = 0  # where inherit and original args separated.
        self.var_name_idx = 0  # record idx where is arg: var_name

    def set_header_labels(self, header1: str, header2: str):
        # only two headers available
        self.setHorizontalHeaderLabels((header1, header2))

    def _get_inherit_args(self):
        for i, arg in self.db.get_inh_args(self.inherit):
            self.feed_inherit_item(i, arg)
            # add counter
            self.n += 1
        self.io_separator = self.n  # record here

    def _get_original_args(self):
        for i, arg in self.db.get_org_args(self.id_string):
            self.feed_original_item(i + self.n, arg)

    def _get_custom_args(self, count):
        name = ArgNameItem('var',
                           'The name of this variable.',
                           'var_name')
        init_value = self.node_name.lower()
        value = ArgEditItem(init_value if count == 1
                            else init_value + '_' + str(count),
                            'String', 'var_name')
        self.set_col_items(self.n, name, value)
        self.var_name_idx = self.n  # record here
        self.n += 1

    def get_args(self, add_custom_args=False, count=1):
        # call this method to get all the args
        if self.inherit:
            self._get_inherit_args()
        if add_custom_args:
            self._get_custom_args(count)
        if self.id_string:
            self._get_original_args()

    def feed_inherit_item(self, idx, unpack_item):
        raise NotImplementedError

    def feed_original_item(self, idx, unpack_item):
        raise NotImplementedError

    def set_col_items(self, col_idx, *items):
        for i, item in enumerate(items):
            self.setItem(col_idx, i, item)

    def items(self):
        """ Generator: yield items in model. """
        idx = 0
        while True:
            arg_name_item = self.item(idx, 0)
            if arg_name_item is None:
                break
            arg_value_item = self.item(idx, 1)
            yield idx, arg_name_item, arg_value_item
            idx += 1


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
                 node_type: str,
                 node_id: str,
                 inherit: str):
        super().__init__(db_link, node_name, node_id, inherit)
        # args: combobox style cell
        self.combo_args = []
        # args: check button style cell
        self.check_args = []
        self.node_type = node_type
        # setup semaphore here
        self.rb_semaphore = ReferenceBySemaphore()

        # set header labels for this model
        self.set_header_labels("Name", "Argument Value")

    @property
    def var_name(self):
        return self.item(self.var_name_idx, 1).text()

    @property
    def var_name_item(self):
        return self.item(self.var_name_idx, 1)

    # ------OPTIONAL PROPERTY------
    # Maintain the rb_semaphore by property ref_by.

    def set_ref_by(self, ref_by: tuple):
        # ref_by is instance of ArgEditItem.
        self.rb_semaphore.add(ref_by)
        self.rb_semaphore.update_flag = True

    def get_ref_by(self):
        return self.rb_semaphore.get()

    def del_ref_by(self):
        self.rb_semaphore.destroy()

    ref_by = property(get_ref_by, set_ref_by, del_ref_by)

    # -----------------------------

    def reassign_value(self, idx, value: str):
        # reassign the value in args combobox.
        arg_item = self.item(idx, 1)
        arg_item.value = value
        arg_item.has_changed()

    def reassign_state(self, idx, state: str):
        arg_item = self.item(idx, 1)
        arg_item.value = state
        arg_item.is_changed = ~arg_item.is_changed

    def feed_inherit_item(self, idx, unpack_item):
        # id, name, init, type, info
        _, arg_name, arg_init, arg_type, arg_info = unpack_item
        arg_type_item = ArgTypeItem(arg_type)
        arg_name_item = ArgNameItem('inh', arg_info, arg_name)
        if arg_type == "bool":
            arg_mark_item = ArgEditItem(arg_init,
                                        dtype=arg_type_item.raw_type_name,
                                        belong_to=arg_name,
                                        tag=1,
                                        store_bg=True)
            self.check_args.append(idx)
            self.set_col_items(idx, arg_name_item, arg_mark_item)
        else:
            arg_init_item = ArgEditItem(arg_init,
                                        dtype=arg_type_item.raw_type_name,
                                        belong_to=arg_name)
            self.set_col_items(idx, arg_name_item, arg_init_item)

    def feed_original_item(self, idx, unpack_item):
        # id, note, name, init, type, info, box
        _, _, arg_name, arg_init, arg_type, arg_info, arg_box = unpack_item
        arg_type_item = ArgTypeItem(arg_type)
        arg_name_item = ArgNameItem('org', arg_info, arg_name)
        if arg_box:
            # setup the combo box for box args
            arg_box_list = self.db.get_box_args(int(arg_box)).split(';')
            self.combo_args.append([idx, arg_init, arg_box_list])
            # placeholder is where to store the current value
            arg_mark_item = ArgEditItem(arg_init,
                                        dtype=arg_type_item.raw_type_name,
                                        belong_to=arg_name,
                                        tag=2, store_bg=True)
            self.set_col_items(idx, arg_name_item, arg_mark_item)
        elif arg_type == "bool":
            # setup the check button for bool type
            arg_mark_item = ArgEditItem(arg_init,
                                        dtype=arg_type_item.raw_type_name,
                                        belong_to=arg_name,
                                        tag=1, store_bg=True)
            self.check_args.append(idx)
            self.set_col_items(idx, arg_name_item, arg_mark_item)
        else:
            arg_init_item = ArgEditItem(arg_init,
                                        dtype=arg_type_item.raw_type_name,
                                        belong_to=arg_name)
            self.set_col_items(idx, arg_name_item, arg_init_item)
