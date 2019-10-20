from PyQt5.QtWidgets import QTableView, QHeaderView, QCheckBox
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt

from lib import DataBase4Args
from editor.component.args_model import ArgsPreviewModel, ArgsEditableModel
from editor.component.args_model_item import ArgComboBox


class KMBNodesArgsMenu(QTableView):

    def __init__(self,
                 menu_delegate,
                 parent=None):
        super().__init__(parent)

        self.menu = menu_delegate  # self wrapper
        self.head = QHeaderView(Qt.Horizontal, self)
        # link to database
        self.db_link = DataBase4Args()
        self.null_model = QStandardItemModel()
        # for collection the ArgsEditableModel
        self.edit_model = {}

        # set the horizontal head
        self.head.setStretchLastSection(True)
        self.setHorizontalHeader(self.head)
        # hide the vertical head
        self.verticalHeader().setHidden(True)
        # set width
        self.setMinimumWidth(320)

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
            model = self.edit_model[node_id]
            self.setModel(model)
            # try to set combo box args
            if model.combo_args:
                self.add_combobox_cell(model)
            # try to set check button args
            if model.check_args:
                self.add_checkbox_cell(model)
            model.itemChanged.connect(self.modify_item)
        except KeyError:
            self.setModel(self.null_model)

    def add_combobox_cell(self, model):
        # clean the widgets id, every time click node,
        # it will generate new ids.
        model.combo_widgets_id.clear()
        for row, col, arg_init, args_list, arg_set, _ in model.combo_args:
            index = self.model().index(row, col)
            combo = ArgComboBox(args_list, arg_init)
            # set current new value
            if arg_set != "placeholder":
                combo.setCurrentText(arg_set)
            model.combo_widgets_id.append(id(combo))
            self.setIndexWidget(index, combo)
            combo.currentTextChanged.connect(lambda v: self.modify_args(v, combo, model))

    def add_checkbox_cell(self, model):
        model.check_widgets_id.clear()
        for row, col, arg_init, _ in model.check_args:
            index = self.model().index(row, col)
            check = QCheckBox(arg_init)
            # initialize the checkbox
            if arg_init == "True":
                check.setChecked(True)
            else:
                check.setChecked(False)
            model.check_widgets_id.append(id(check))
            self.setIndexWidget(index, check)
            check.clicked.connect(lambda s: self.modify_state(s, model))

    def modify_item(self, item):
        item.has_changed()
        item.setText(item.text())

    def modify_args(self, value, combo, model):
        # set the model's placeholder in combo_args
        if model.combo_widgets_id.__contains__(id(combo.sender())):
            idx = model.combo_widgets_id.index(id(combo.sender()))
            model.reassign_value(idx, value)
        else:
            model.reassign_value(-1, value)

    def modify_state(self, state, model):
        idx = model.check_widgets_id.index(id(self.sender()))
        model.reassign_state(idx, str(state))
        self.sender().setText(str(state))

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
