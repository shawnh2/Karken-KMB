from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt

from editor.component.args_model import ArgsPreviewModel, ArgsEditableModel
from editor.component.args_model_item import ArgComboBox, ArgCheckBox
from lib import DataBase4Args, debug


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
        value = item.text()
        if item.is_referenced:
            # avoid referenced here
            pass
        else:
            item.setText(value)
            if item.check_changed(value):
                item.has_changed()
            else:
                item.undo_change()
        # if this is where var_name got changed,
        # also change value where nodes referenced with.
        if self.current_model.ref_by_update:
            self.current_model.update_ref_by(value)

    def modify_args(self, value):
        # TODO: combo add ref and del
        # TODO: one ref edge del case
        self.current_model.reassign_value(self.sender().at, value)

    def modify_state(self, state):
        self.current_model.reassign_state(self.sender().at, str(state))
        self.sender().setText(str(state))

    def modify_ref(self, dst_node_id, idx, src_node_id):
        # create ref here
        dst_model = self.edit_model.get(dst_node_id)
        src_model = self.edit_model.get(src_node_id)
        dst_value_item = dst_model.item(idx, 1)
        src_value_item = src_model.item(src_model.var_name_idx, 1)
        # save the relationship of ref
        dst_value_item.ref_to = src_value_item
        src_model.ref_by = dst_value_item

        item_name = dst_model.item(idx, 0).text()
        debug(f'[REF] create <{dst_model.node_name}>:{dst_model.var_name}.{item_name} '
              f'~ <{src_model.node_name}>:{src_model.var_name}')

    # ------Operations on Node Model------

    def commit_node(self,
                    node_name, node_type,
                    node_id: str, count: int):
        # after adding node in canvas
        # first time make new model.
        id_string, inherit = self.db_link.get_args_id(node_name)
        model = ArgsEditableModel(
            db_link=self.db_link,
            node_name=node_name,
            node_type=node_type,
            node_id=id_string,
            inherit=inherit
        )
        model.get_args(add_custom_args=True, count=count)
        # then store it but don't display it.
        self.edit_model[node_id] = model

    def delete_node(self, node_id: str):
        model = self.edit_model.get(node_id)
        # remove the ref
        if model.node_name == 'PlaceHolder':
            del model.ref_by
        # remove entire node item
        self.edit_model.__delitem__(node_id)
        self.setModel(self.null_model)

    def fetch_node(self, node_id: str):
        # get the arg model by id.
        return self.edit_model.get(node_id)
