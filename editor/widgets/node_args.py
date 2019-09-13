import sqlite3

from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import Qt

from lib import split_args_id, type_color_map


DATABASE = sqlite3.connect('lib/node.db')
CURSOR = DATABASE.cursor()


class KMBNodesArgsMenu(QTableView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.args = None
        self.head = QHeaderView(Qt.Horizontal, self)

        # set the horizontal head
        self.head.setStretchLastSection(True)
        self.setHorizontalHeader(self.head)
        # hide the vertical head
        self.verticalHeader().setHidden(True)
        # set width
        self.setFixedWidth(300)

    def load_args_by_name(self, node_name):
        res = CURSOR.execute('SELECT ORI_ARGS, INH_ARGS FROM '
                             f'nodes WHERE NAME="{node_name}"')
        id_string, inherit = res.fetchone()

        self.set_args(inherit, id_string)

    def set_args(self, inherit, id_string):
        self.args = ArgItemsPreviewModel(id_string, inherit)
        self.args.set_all_args()
        self.setModel(self.args)


class ArgItemsPreviewModel(QStandardItemModel):

    def __init__(self, id_string: str, inherit: str):
        super().__init__()
        self.id_string = id_string
        self.inherit = inherit
        self.n = 0

        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(['Type', 'Argument name'])

    def set_original_args(self):
        split_id = split_args_id(self.id_string)
        for i, id_ in enumerate(split_id):
            res = CURSOR.execute(f'SELECT * FROM org_args WHERE ID={id_}')
            _, _, arg_name, _, arg_type, arg_info, _ = res.fetchone()
            # set original args to table
            arg_name_item = NodeArgNameItem(arg_name,
                                            mode='org', tool_tip=arg_info)
            arg_type_item = NodeArgTypeItem(arg_type)
            self.setItem(i + self.n, 0, arg_type_item)
            self.setItem(i + self.n, 1, arg_name_item)

    def set_inherit_args(self):
        res = CURSOR.execute(f'SELECT * FROM inh_args WHERE ID={self.inherit}')
        for i, arg in enumerate(res.fetchall()):
            _, arg_name, _, arg_type, arg_info = arg
            # set inherit args to table
            arg_name_item = NodeArgNameItem(arg_name,
                                            mode='inh', tool_tip=arg_info)
            arg_type_item = NodeArgTypeItem(arg_type)
            self.setItem(i, 0, arg_type_item)
            self.setItem(i, 1, arg_name_item)
            # add into counter
            self.n += 1

    def set_all_args(self):
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
