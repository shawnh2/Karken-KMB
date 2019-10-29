from PyQt5.QtWidgets import QTableView, QHeaderView, QAction, QMenu
from PyQt5.QtGui import QStandardItemModel, QContextMenuEvent, QCursor
from PyQt5.QtCore import Qt, pyqtSignal

from editor.component.args_model import ArgsPreviewModel, ArgsEditableModel
from editor.component.args_model_item import ArgComboBox, ArgCheckBox
from lib import DataBase4Args, debug, AutoInspector


class KMBNodesArgsMenu(QTableView):

    the_rest_ref_items = pyqtSignal(int)  # count
    do_not_pick_one = pyqtSignal(bool)    # boolean

    def __init__(self,
                 menu,
                 parent=None):
        super().__init__(parent)

        self.menu = menu  # self wrapper
        self.head = QHeaderView(Qt.Horizontal, self)
        # link to database
        self.db_link = DataBase4Args()
        self.null_model = QStandardItemModel()
        # checking the value by its type.
        self.inspector = AutoInspector()
        # for collection the ArgsEditableModel
        self.edit_model = {}
        self.current_model = None
        self.current_ref_model = None
        self.current_ref_dst_model_id = None

        # set the horizontal head
        self.head.setStretchLastSection(True)
        self.setHorizontalHeader(self.head)
        # hide the vertical head
        self.verticalHeader().setHidden(True)
        # set width
        self.setMinimumWidth(320)
        self.setMaximumWidth(500)
        # set pop up right menu policy
        self.right_menu = QMenu()
        self.setContextMenuPolicy(Qt.DefaultContextMenu)

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
            # there's a editable item behind it.
            item = self.current_model.item(row, 1)
            cur_value = item.value
            # this item store the current value,
            # grab it and set to current text.
            # if the value is out of the combo box,
            # which means this a ref value, and add it,
            # then set to current value again.
            if not args_list.__contains__(cur_value):
                # make a copy of args_list, so won't mess
                # up with those original values.
                copy_args_list = args_list.copy()
                copy_args_list.append(cur_value)
                combo = ArgComboBox(copy_args_list, arg_init, at=row)
            else:
                combo = ArgComboBox(args_list, arg_init, at=row)
            combo.setCurrentText(cur_value)
            self.setIndexWidget(index, combo)
            combo.currentTextChanged.connect(self.modify_args)

    def add_checkbox_cell(self):
        for row in self.current_model.check_args:
            index = self.model().index(row, 1)
            item = self.current_model.item(row, 1)
            check = ArgCheckBox(item.value, at=row)
            self.setIndexWidget(index, check)
            check.clicked.connect(self.modify_state)

    def modify_item(self, item):
        value = item.text()
        if item.is_referenced:
            # avoid referenced item here nor bug.
            pass
        else:
            checked_value = self.inspector.auto_type_check(value, item.dtype)
            item.value = checked_value
            if item.check_changed(value):
                item.has_changed()
            else:
                item.undo_change()
        # if this is where var_name got changed,
        # also change value where nodes referenced with.
        if self.current_model.ref_by_update_flag:
            self.current_model.update_ref_by(value)
            # ! close the trigger here nor RecursionException here.
            self.current_model.ref_by_update_flag = False

    def modify_args(self, value):
        self.current_model.reassign_value(self.sender().at, value)

    def modify_state(self, state):
        self.current_model.reassign_state(self.sender().at, str(state))
        self.sender().value = str(state)

    def modify_ref(self, dst_node_id, idx, src_node_id):
        # create ref here
        dst_model = self.edit_model.get(dst_node_id)
        src_model = self.edit_model.get(src_node_id)
        dst_value_item = dst_model.item(idx, 1)
        src_value_item = src_model.item(src_model.var_name_idx, 1)
        # save the relationship of ref
        dst_value_item.ref_to = src_value_item
        # dst node model id, and dst value edit item.
        src_model.ref_by = (dst_node_id, dst_value_item)

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

    # ------Operations on Edge Model------

    def delete_ref_related(self, src_model_id: str, dst_model_id: str):
        # while deleting ref edge will trigger this method only.
        # through ref_id will get the model of ref edge's start item.
        self.current_ref_model = self.edit_model.get(src_model_id)
        self.current_ref_dst_model_id = dst_model_id
        # if one start item connected with one node item.
        # under this situation, just del the ref_by.
        if self.current_ref_model.count_ref_items(dst_model_id) == 1:
            del self.current_ref_model.ref_by
            # single connected ref edge still needs these signals.
            self.the_rest_ref_items.emit(0)
            self.do_not_pick_one.emit(False)
        # if one start item connected with one node but multi items.
        # then pop up a menu to decide which edge.
        else:
            fake_event = QContextMenuEvent(QContextMenuEvent.Mouse, QCursor.pos())
            self.contextMenuEvent(fake_event)

    def delete_rm_selected(self):
        # deleted the one item that selected in right menu.
        ref_item_id = self.sender().objectName()
        self.current_ref_model.remove_ref_by(self.current_ref_dst_model_id, ref_item_id)
        # if one ref node has multi ref edges linked to one node,
        # view will only display one of the edges.
        # so do not delete ref edge until there's no edge left.
        rest_ref_edge_count = self.current_ref_model.count_ref_items(self.current_ref_dst_model_id)
        self.the_rest_ref_items.emit(rest_ref_edge_count)
        # what if do not pick one from right menu.
        self.do_not_pick_one.emit(False)

    def contextMenuEvent(self, event):
        # set header of right menu
        header = QAction('Choose one reference to remove')
        header.setEnabled(False)
        self.right_menu.addAction(header)
        self.right_menu.addSeparator()
        # set content of right menu
        actions = []
        model = self.current_ref_model.ref_by.get(self.current_ref_dst_model_id)
        for ref_id, ref_item in model.items():
            action = QAction(ref_item.belong_to)
            action.setObjectName(f'{ref_id}')
            action.triggered.connect(self.delete_rm_selected)
            actions.append(action)
        self.right_menu.addActions(actions)
        # show right menu
        self.right_menu.exec(QCursor.pos())
