from collections import OrderedDict

from PyQt5.QtGui import QStandardItemModel

from editor.component.args_model_item import ArgNameItem, ArgTypeItem, ArgEditItem
from editor.component.semaphores import ReferenceBySemaphore, ModelIOSemaphore
from lib import pin_args_dict, type_tag_map


class ArgsSuperModel(QStandardItemModel):

    AUTO_COUNT_NAME = (
        'Input', 'Model', 'PlaceHolder'
    )  # nodes that its var_name is auto increasing.

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

    @property
    def var_name(self):
        return self.item(self.var_name_idx, 1).text()

    @property
    def var_name_item(self):
        return self.item(self.var_name_idx, 1)

    def set_var_name(self, var_name: str):
        self.var_name_item.value = var_name

    def set_header_labels(self, header1: str, header2: str):
        # only two headers available
        self.setHorizontalHeaderLabels((header1, header2))

    def _get_inherit_args(self, count):
        for i, arg in self.db.get_inh_args(self.inherit):
            self.feed_inherit_item(i, arg, count)
            # add counter
            self.n += 1
        self.io_separator = self.n  # record here

    def _get_original_args(self):
        for i, arg in self.db.get_org_args(self.id_string):
            self.feed_original_item(i + self.n, arg)

    def _get_custom_args(self, count):
        name = ArgNameItem('var', 'The variable name of this node.',
                           'var_name')
        var_name = self.node_name.lower()
        if self.node_name in self.AUTO_COUNT_NAME:
            var_name += (f'_{count}' if count > 1 else '')
        else:
            pass
        value = ArgEditItem(var_name, 'String', 'var_name')
        self.set_col_items(self.n, name, value)
        self.var_name_idx = self.n  # record here
        self.n += 1

    def get_args(self, add_custom_args=False, count=1):
        # call this method to get all the args
        if self.inherit:
            self._get_inherit_args(count)
        if add_custom_args:
            self._get_custom_args(count)
        if self.id_string:
            self._get_original_args()

    def feed_inherit_item(self, idx, unpack_item, count):
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

    def get_item_by_name(self, name: str):
        # get the first item by name.
        for idx, name_item, value_item in self.items():
            if name_item.text() == name:
                return idx, value_item
        return None


class ArgsPreviewModel(ArgsSuperModel):

    def __init__(self,
                 db_link,
                 node_name: str,
                 node_id: str,
                 inherit: str):
        super().__init__(db_link, node_name, node_id, inherit)
        # set header labels for this model
        self.set_header_labels("Type", "Argument Name")

    def feed_inherit_item(self, idx, unpack_item, _):
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
                 inherit: str,
                 pin_args: str):
        super().__init__(db_link, node_name, node_id, inherit)
        # args: combobox style cell
        self.combo_args = []
        # args: check button style cell
        self.check_args = []
        # args: io order style cell
        self.io_order_args = []
        # args: for pin args
        if pin_args != 'None':
            self.pin_args = pin_args_dict(pin_args)
        else:
            self.pin_args = None

        self.node_type = node_type
        # setup semaphore here
        self.rb_semaphore = ReferenceBySemaphore()
        self.io_semaphore = ModelIOSemaphore(self)

        # set header labels for this model
        self.set_header_labels("Name", "Argument Value")

    # ------MAINTAIN SEMAPHORE------
    # Maintain the rb_semaphore by property ref_by.

    def set_ref_by(self, ref_by: tuple):
        self.rb_semaphore.add(ref_by)
        self.rb_semaphore.update_flag = True

    def get_ref_by(self):
        return self.rb_semaphore.get()

    def del_ref_by(self):
        self.rb_semaphore.destroy()

    ref_by = property(get_ref_by, set_ref_by, del_ref_by)

    # Maintain the io_semaphore by property io.

    def set_io(self, io: tuple):
        # io: src_node_id, sign, src_node_var_name_item
        self.io_semaphore.add(io)

    def get_io(self):
        return self.io_semaphore.get()

    io = property(get_io, set_io)

    # -----------------------------

    @classmethod
    def reassign_value(cls, item, value: str) -> bool:
        # reassign item's value and
        # return whether value has been changed.
        item.value = value
        if item.check_changed(value):
            item.has_changed()
            return True
        else:
            item.undo_change()
            return False

    def reassign_item(self, idx, value: str):
        # reassign the item in args combobox.
        arg_item = self.item(idx, 1)
        arg_item.value = value
        arg_item.has_changed()

    def reassign_state(self, idx, state: str):
        arg_item = self.item(idx, 1)
        arg_item.value = state
        arg_item.is_changed = ~arg_item.is_changed

    def feed_inherit_item(self, idx, unpack_item, count):
        # id, name, init, type, info
        _, arg_name, arg_init, arg_type, arg_info = unpack_item
        # inherit item doesn't have any required args.
        pin_marker = False
        arg_type_item = ArgTypeItem(arg_type)  # provide dtype for each arg item.
        arg_name_item = ArgNameItem('inh', arg_info, arg_name)
        # auto increase the arg 'name' value.
        if arg_name == 'name':
            arg_init = f'{self.node_name.lower()}_{count}'
        # replace org value with pin value if it has.
        pin_value = self.feed_with_pins(arg_name)
        if pin_value is not None:
            arg_init = pin_value
            pin_marker = True
        # set arg value with different types.
        if arg_type == "bool":
            arg_mark_item = ArgEditItem(arg_init,
                                        dtype=arg_type_item.raw_type_name,
                                        belong_to=arg_name,
                                        tag=1,
                                        store_bg=True,
                                        is_pined=pin_marker)
            self.check_args.append(idx)
            self.set_col_items(idx, arg_name_item, arg_mark_item)
        else:
            arg_init_item = ArgEditItem(arg_init,
                                        dtype=arg_type_item.raw_type_name,
                                        belong_to=arg_name,
                                        is_pined=pin_marker)
            self.set_col_items(idx, arg_name_item, arg_init_item)

    def feed_original_item(self, idx, unpack_item):
        # id, note, name, init, type, info, box
        _, _, arg_name, arg_init, arg_type, arg_info, arg_box = unpack_item
        pin_marker = False
        is_required = False
        arg_type_item = ArgTypeItem(arg_type)
        arg_name_item = ArgNameItem('org', arg_info, arg_name)
        pin_value = self.feed_with_pins(arg_name)
        if pin_value is not None:
            arg_init = pin_value
            pin_marker = True
        if arg_init is None:
            is_required = True
        if arg_box:
            # setup the combo box for box args
            arg_box_list = self.db.get_box_args(int(arg_box)).split(';')
            self.combo_args.append([idx, arg_init, arg_box_list])
            # placeholder is where to store the current value
            arg_mark_item = ArgEditItem(arg_init,
                                        dtype=arg_type_item.raw_type_name,
                                        belong_to=arg_name,
                                        tag=2,
                                        store_bg=True,
                                        is_pined=pin_marker,
                                        is_required=is_required)
            self.set_col_items(idx, arg_name_item, arg_mark_item)
        elif arg_type == "bool":
            # setup the check button for bool type
            arg_mark_item = ArgEditItem(arg_init,
                                        dtype=arg_type_item.raw_type_name,
                                        belong_to=arg_name,
                                        tag=1,
                                        store_bg=True,
                                        is_pined=pin_marker,
                                        is_required=is_required)
            self.check_args.append(idx)
            self.set_col_items(idx, arg_name_item, arg_mark_item)
        elif self.node_name == 'Model' and arg_name in ('inputs', 'outputs'):
            # setup for model io order panel
            arg_order_item = ArgEditItem(arg_init,
                                         dtype=arg_type_item.raw_type_name,
                                         belong_to=arg_name,
                                         tag=3,
                                         store_bg=True,
                                         is_required=is_required)
            self.io_order_args.append(idx)
            self.set_col_items(idx, arg_name_item, arg_order_item)
        else:
            arg_init_item = ArgEditItem(arg_init,
                                        dtype=arg_type_item.raw_type_name,
                                        belong_to=arg_name,
                                        is_pined=pin_marker,
                                        is_required=is_required)
            self.set_col_items(idx, arg_name_item, arg_init_item)

    def feed_with_pins(self, org_name):
        # return the pin value of this org arg name.
        if self.pin_args is None:
            return None
        # return result may be None or value.
        return self.pin_args.get(org_name)

    def extract_args(self,
                     get_changed=False,
                     get_referenced=False,
                     get_required=False,
                     get_io=False,
                     get_pined=False,
                     get_datatype=False,
                     get_var_name=False):
        # extract all the args from model and
        # wrap all of them in OrderDict then return.
        arg_dict = OrderedDict()
        # get all the args by conditions.
        for idx, arg_name, arg_value in self.items():
            # whether pass the var_name arg item.
            if arg_name.text() == 'var_name' and not get_var_name:
                continue
            dtype = type_tag_map(arg_value)
            # get changed.
            if arg_value.is_changed and get_changed:
                arg_dict[arg_name.text()] = (arg_value.value, dtype)\
                    if get_datatype else arg_value.value
            # get referenced.
            elif arg_value.is_referenced and get_referenced:
                arg_dict[arg_name.text()] = (arg_value.ref_to, dtype)\
                    if get_datatype else arg_value.ref_to
            # get required.
            elif arg_value.is_required and get_required:
                arg_dict[arg_name.text()] = (arg_value.value, dtype)\
                    if get_datatype else arg_value.value
            # get pined.
            elif arg_value.is_pined and get_pined:
                arg_dict[arg_name.text()] = (arg_value.value, dtype)\
                    if get_datatype else arg_value.value
            # else ...
        if self.node_name == 'Model' and get_io:
            inputs, outputs = self.io
            arg_dict['inputs'] = (list(inputs.keys()), 'id')\
                if get_datatype else list(inputs.keys())
            arg_dict['outputs'] = (list(outputs.keys()), 'id')\
                if get_datatype else list(outputs.keys())
        return arg_dict

    def extract_pin(self):
        # extract necessary info for pin.
        pin_args = ";".join([f'{arg_name}={arg_value}'
                             for arg_name, arg_value in
                             self.extract_args(get_changed=True,
                                               get_pined=True).items()])
        return pin_args, self.node_name
