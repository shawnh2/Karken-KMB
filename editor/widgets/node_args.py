import sqlite3

from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import Qt

from lib import split_args_id, type_color_map


DATABASE = sqlite3.connect('lib/node.db')
CURSOR = DATABASE.cursor()


class KMBNodesArgsMenu(QTableView):

    def __init__(self, menu_delegate, parent=None):
        super().__init__(parent)

        self.args_model = None
        self.menu = menu_delegate
        self.head = QHeaderView(Qt.Horizontal, self)

        # set the horizontal head
        self.head.setStretchLastSection(True)
        self.setHorizontalHeader(self.head)
        # hide the vertical head
        self.verticalHeader().setHidden(True)
        # set width
        self.setFixedWidth(300)

    @classmethod
    def load_args_by_name(cls, node_name):
        res = CURSOR.execute('SELECT ORI_ARGS, INH_ARGS FROM '
                             f'nodes WHERE NAME="{node_name}"')
        id_string, inherit = res.fetchone()
        return id_string, inherit

    def set_preview_args(self, node_name):
        id_string, inherit = self.load_args_by_name(node_name)
        self.args_model = ArgItemsModel(id_string, inherit, 'view')
        self.setModel(self.args_model)

    def set_editing_args(self, node_name):
        id_string, inherit = self.load_args_by_name(node_name)
        self.args_model = ArgItemsModel(id_string, inherit, 'edit')
        self.setModel(self.args_model)
        # add item changed listener.
        self.args_model.itemChanged.connect(self.menu.collect_change)


class ArgItemsModel(QStandardItemModel):

    def __init__(self,
                 id_string: str,
                 inherit: str,
                 mode: str):
        super().__init__()
        assert mode in ('view', 'edit')

        self.id_string = id_string
        self.inherit = inherit
        self.mode = mode

        self.n = 0
        self.header = []

        # init headers by mode
        self.init_headers()
        # init the arg items of menu
        self.init_arg_items()

    def init_headers(self):
        if self.mode == 'view':
            self.setHorizontalHeaderLabels(
                ('Type',
                 'Argument name')
            )
        else:
            self.setHorizontalHeaderLabels(
                ('Argument name',
                 'Argument value')
            )

    def set_original_args(self):
        split_id = split_args_id(self.id_string)
        for i, id_ in enumerate(split_id):
            res = CURSOR.execute(f'SELECT * FROM org_args WHERE ID={id_}')
            self.add_item(i + self.n, res.fetchone(), 'org')

    def set_inherit_args(self):
        res = CURSOR.execute(f'SELECT * FROM inh_args WHERE ID={self.inherit}')
        for i, arg in enumerate(res.fetchall()):
            self.add_item(i, arg, 'inh')
            # add counter
            self.n += 1

    def add_item(self, idx, unpack_item, unpack_mode):
        if unpack_mode == 'inh':
            # id, name, init, type, info
            _, arg_name, arg_init, arg_type, arg_info = unpack_item
        else:  # 'org'
            # id, note, name, init, type, info, box
            _, _, arg_name, arg_init, arg_type, arg_info, _ = unpack_item

        arg_name_item = NodeArgNameItem(arg_name,
                                        mode=unpack_mode,
                                        tool_tip=arg_info)
        if self.mode == 'view':
            arg_type_item = NodeArgTypeItem(arg_type)
            self.setItem(idx, 0, arg_type_item)
            self.setItem(idx, 1, arg_name_item)
        else:  # 'edit'
            arg_edit_item = NodeArgEditItem(arg_init, arg_name)
            self.setItem(idx, 0, arg_name_item)
            self.setItem(idx, 1, arg_edit_item)

    def init_arg_items(self):
        if self.inherit is not None:
            self.set_inherit_args()
        if self.id_string is not None:
            self.set_original_args()


class NodeArgNameItem(QStandardItem):

    def __init__(self, *args, mode=None, tool_tip=None):
        super().__init__(*args)

        assert mode in ('inh', 'org')
        self.mode = mode

        if self.mode == 'inh':
            self.setBackground(QColor('#BFEFFF'))
        else:
            self.setBackground(QColor('#FFE4B5'))

        self.setEditable(False)
        self.setToolTip(tool_tip)


class NodeArgTypeItem(QStandardItem):

    def __init__(self, args):
        type_string = args
        type_color, raw_type_name = type_color_map(type_string)

        super().__init__(raw_type_name)
        self.setBackground(QColor(type_color))

        self.setEditable(False)


class NodeArgEditItem(QStandardItem):

    def __init__(self, *args):
        self.initial_value, self.arg_name = args
        super().__init__(self.initial_value)

        self.setEditable(True)
