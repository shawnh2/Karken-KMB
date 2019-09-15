from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import Qt

from lib import type_color_map, DataBase4Args
from cfg import color


class KMBNodesArgsMenu(QTableView):

    def __init__(self,
                 menu_delegate,
                 parent=None):
        super().__init__(parent)

        self.menu = menu_delegate
        self.head = QHeaderView(Qt.Horizontal, self)
        # link to database
        self.db_link = DataBase4Args()
        self.null_model = QStandardItemModel()
        self.edit_model = {}  # for collection

        # set the horizontal head
        self.head.setStretchLastSection(True)
        self.setHorizontalHeader(self.head)
        # hide the vertical head
        self.verticalHeader().setHidden(True)
        # set width
        self.setFixedWidth(300)

    def set_preview_args(self, node_name):
        id_string, inherit = self.db_link.get_args_id(node_name)
        preview_model = ArgItemsModel(
            self.db_link, id_string, inherit, 'view'
        )
        preview_model.set_preview_model()
        self.setModel(preview_model)

    def set_editing_args(self, node_name, node_id):
        if node_name == 'empty':
            # set an empty model.
            self.setModel(self.null_model)
            return

        if self.edit_model.__contains__(node_id):
            # load args that already exists.
            model = self.edit_model[node_id]
            self.setModel(model)
        else:
            # first time make new model.
            id_string, inherit = self.db_link.get_args_id(node_name)
            model = ArgItemsModel(
                self.db_link, id_string, inherit, 'edit'
            )
            model.set_editing_model()
            # then store it and display.
            self.edit_model[node_id] = model
            self.setModel(model)

        model.itemChanged.connect(self.modify_model)

    def modify_model(self, item):
        item.has_changed()
        item.setText(item.text())


class ArgItemsModel(QStandardItemModel):

    def __init__(self,
                 db_link,
                 id_string: str,
                 inherit: str,
                 mode: str):
        super().__init__()

        self.db = db_link
        self.id_string = id_string
        self.inherit = inherit
        self.mode = mode
        self.n = 0

        assert self.mode in ('view', 'edit')

    def set_preview_model(self):
        self.setHorizontalHeaderLabels(('Type', 'Argument name'))
        # init the arg items of menu
        self.get_args()

    def set_editing_model(self):
        self.setHorizontalHeaderLabels(('Argument name', 'Argument value'))
        self.get_args()

    def get_args(self):
        if self.inherit is not None:
            self.get_inherit_args()
        if self.id_string is not None:
            self.get_original_args()

    def get_original_args(self):
        for i, arg in self.db.get_org_args(self.id_string):
            self.feed_item(i + self.n, arg, 'org')

    def get_inherit_args(self):
        for i, arg in self.db.get_inh_args(self.inherit):
            self.feed_item(i, arg, 'inh')
            # add counter
            self.n += 1

    def feed_item(self,
                  idx,
                  unpack_item,
                  unpack_mode):

        if unpack_mode == 'inh':
            # id, name, init, type, info
            _, arg_name, arg_init, arg_type, arg_info = unpack_item
        else:  # 'org'
            # id, note, name, init, type, info, box
            _, _, arg_name, arg_init, arg_type, arg_info, _ = unpack_item

        arg_name_item = ArgNameItem(arg_name,
                                    mode=unpack_mode,
                                    tool_tip=arg_info)
        arg_type_item = ArgTypeItem(arg_type)
        if self.mode == 'view':
            self.setItem(idx, 0, arg_type_item)
            self.setItem(idx, 1, arg_name_item)
        else:
            arg_init_item = ArgEditItem(arg_init,
                                        tool_tip=arg_type_item.raw_type_name)
            self.setItem(idx, 0, arg_name_item)
            self.setItem(idx, 1, arg_init_item)


class ArgNameItem(QStandardItem):

    def __init__(self, *args, mode=None, tool_tip=None):
        super().__init__(*args)

        assert mode in ('inh', 'org')
        self.mode = mode

        if self.mode == 'inh':
            self.setBackground(QColor(color['INH_ARG']))
        else:
            self.setBackground(QColor(color['ORG_ARG']))

        self.setEditable(False)
        self.setToolTip(tool_tip)


class ArgTypeItem(QStandardItem):

    def __init__(self, args):
        self.type_string = args
        self.type_color, self.raw_type_name = \
            type_color_map(self.type_string)

        super().__init__(self.raw_type_name)
        self.setBackground(QColor(self.type_color))

        self.setEditable(False)


class ArgEditItem(QStandardItem):

    def __init__(self, *args, tool_tip=None):
        super().__init__(*args)
        self.is_changed = False

        self.setEditable(True)
        self.setToolTip(tool_tip)

    def has_changed(self):
        self.is_changed = True
        self.setBackground(QColor(color['CHA_ARG']))
