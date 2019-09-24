from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt, QModelIndex

from lib import DataBase4Args
from editor.component.args_model import ArgsPreviewModel, ArgsEditableModel


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
        preview_model = ArgsPreviewModel(self.db_link, id_string, inherit)
        preview_model.get_args()
        self.setModel(preview_model)

    def set_editing_args(self, node_id):
        if node_id == 0:
            # set an empty model.
            self.setModel(self.null_model)
            return
        # load args model that already exists.
        try:
            model = self.edit_model[node_id]
            self.setModel(model)
            # try to set combo box args
            # and must do it after setting model
            # nor the model will cover it again
            if model.combo_args:
                for row, col, combo in model.combo_args:
                    index = self.model().index(row, col)
                    self.setIndexWidget(index, combo)
            model.itemChanged.connect(self.modify_item)
        except KeyError:
            self.setModel(self.null_model)

    def modify_item(self, item):
        item.has_changed()
        item.setText(item.text())

    def commit_node(self, node_name, node_id):
        # after adding node in canvas
        # first time make new model.
        id_string, inherit = self.db_link.get_args_id(node_name)
        model = ArgsEditableModel(self.db_link, id_string, inherit)
        model.get_args()
        # then store it but don't display.
        self.edit_model[node_id] = model

    def delete_node(self, node_id):
        self.edit_model.__delitem__(node_id)
