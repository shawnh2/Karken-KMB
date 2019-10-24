from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt

from cfg import DEBUG
from lib import DataBase4Args
from editor.component.args_model import ArgsPreviewModel, ArgsEditableModel
from editor.component.args_model_item import ArgComboBox, ArgCheckBox


class KMBNodesArgsMenu(QTableView):

    def __init__(self,
                 menu,
                 parent=None):
        super().__init__(parent)

        self.menu = menu  # self wrapper
        self.head = QHeaderView(Qt.Horizontal, self)
        # link to database
        self.db_link = DataBase4Args()
        self.null_model = QStandardItemModel()
        # for collection the ArgsEditableModel
        self.edit_model = {}
        self.current_model = None

        # set the horizontal head
        self.head.setStretchLastSection(True)
        self.setHorizontalHeader(self.head)
        # hide the vertical head
        self.verticalHeader().setHidden(True)
        # set width
        self.setMinimumWidth(320)
        self.setMaximumWidth(500)

    def set_preview_args(self, node_name):
        id_string, inherit = self.db_link.get_args_id(node_name)
        preview_model = ArgsPreviewModel(
            db_link=self.db_link,
            node_name=node_name,
            node_id=id_string,
            inherit=inherit)
        preview_model.get_args()
        self.setModel(preview_model)

    def set_editing_args(self, node_id: str):
        if node_id == 'null':
            # set an empty model.
            self.setModel(self.null_model)
            return
        # load args model that already exists.
        try:
            self.current_model = self.edit_model[node_id]
            self.setModel(self.current_model)
            # try to set combo box args
            if self.current_model.combo_args:
                self.add_combobox_cell()
            # try to set check button args
            if self.current_model.check_args:
                self.add_checkbox_cell()
            self.current_model.itemChanged.connect(self.modify_item)
        except KeyError:
            self.setModel(self.null_model)

    def add_combobox_cell(self):
        for row, arg_init, args_list in self.current_model.combo_args:
            index = self.model().index(row, 1)
            # there's a editable item behind it
            item = self.current_model.item(row, 1)
            # this item store the current value
            combo = ArgComboBox(args_list, arg_init, at=row)
            combo.setCurrentText(item.text())
            self.setIndexWidget(index, combo)
            combo.currentTextChanged.connect(self.modify_args)

    def add_checkbox_cell(self):
        for row in self.current_model.check_args:
            index = self.model().index(row, 1)
            item = self.current_model.item(row, 1)
            check = ArgCheckBox(item.text(), at=row)
            self.setIndexWidget(index, check)
            check.clicked.connect(self.modify_state)

    def modify_item(self, item):
        item.setText(item.text())
        item.has_changed()
        cur_idx = self.current_model.indexFromItem(item).row()
        # if this is where var_name got changed,
        # also change value where nodes referenced with.
        # TODO: change the node that attach to it also.
        if cur_idx == self.current_model.var_name_idx:
            pass

    def modify_args(self, value):
        self.current_model.reassign_value(self.sender().at, value)

    def modify_state(self, state):
        self.current_model.reassign_state(self.sender().at, str(state))
        self.sender().setText(str(state))

    def modify_ref(self, dst_node_id, idx, src_node_id):
        dst_model = self.edit_model.get(dst_node_id)
        src_model = self.edit_model.get(src_node_id)
        item_value = dst_model.item(idx, 1)
        # modify the arg to ref's var name
        item_value.set_ref(src_model)
        if DEBUG:
            item_name = dst_model.item(idx, 0).text()
            print(f'[REF] create <{dst_model.node_name}>:{dst_model.var_name}.{item_name} '
                  f'~ <{src_model.node_name}>:{src_model.var_name}')

    def commit_node(self, node_name, node_id: str, count: int):
        # after adding node in canvas
        # first time make new model.
        id_string, inherit = self.db_link.get_args_id(node_name)
        model = ArgsEditableModel(
            db_link=self.db_link,
            node_name=node_name,
            node_id=id_string,
            inherit=inherit
        )
        model.name = node_name
        model.get_args(add_custom_args=True, count=count)
        # then store it but don't display it.
        self.edit_model[node_id] = model

    def delete_node(self, node_id: str):
        self.edit_model.__delitem__(node_id)
        self.setModel(self.null_model)

    def fetch_node(self, node_id: str):
        # get the arg model by id.
        return self.edit_model.get(node_id)
