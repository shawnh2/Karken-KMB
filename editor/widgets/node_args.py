from PyQt5.QtWidgets import QTableView, QHeaderView, QAction, QMenu
from PyQt5.QtGui import QStandardItemModel, QContextMenuEvent, QCursor
from PyQt5.QtCore import Qt, pyqtSignal

from editor.component.args_model import ArgsPreviewModel, ArgsEditableModel
from editor.component.args_model_item import ArgComboBox, ArgCheckBox
from lib import DataBase4Args, debug, AutoInspector


class KMBNodesArgsMenu(QTableView):

    REST_REF_ITEMS_COUNT = pyqtSignal(int)     # count
    WAS_DONE_PICKING_ONE = pyqtSignal(bool)    # boolean

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
        self.setMaximumWidth(520)
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
            if cur_value != '' and not\
               args_list.__contains__(cur_value):
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

    # ------Operations on Model Arg Item------

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
        self.current_model.rb_semaphore.update(value)

    def modify_args(self, value):
        self.current_model.reassign_value(self.sender().at, value)

    def modify_state(self, state):
        self.current_model.reassign_state(self.sender().at, str(state))
        self.sender().setText(str(state))

    def modify_ref(self, dst_node_id, idx, src_node_id):
        # create ref here.
        dst_model = self.edit_model.get(dst_node_id)
        src_model = self.edit_model.get(src_node_id)
        dst_value_item = dst_model.item(idx, 1)
        src_value_item = src_model.item(src_model.var_name_idx, 1)
        # save the relationship of ref and its node id.
        dst_value_item.ref_to = (src_node_id, src_value_item)
        # dst node id, and dst value edit item,
        # and the item of dst model's var name.
        src_model.ref_by = (dst_node_id, dst_value_item,
                            dst_model.var_name_item)

        item_name = dst_model.item(idx, 0).text()
        debug(f'[REF] create <{dst_model.node_name}>:{dst_model.var_name}.{item_name} '
              f'~ <{src_model.node_name}>:{src_model.var_name}')

    def modify_io(self, model_id, io_sign, src_node_id):
        # create io here.
        # only Model will collect I/O, other node won't.
        dst_model = self.edit_model.get(model_id)
        src_model = self.edit_model.get(src_node_id)
        src_value_item = src_model.item(src_model.var_name_idx, 1)
        # load in IO semaphore by io.
        dst_model.io = (src_node_id, io_sign, src_value_item)

    # ------Operations on Node Model------

    def commit_node(self,
                    node_name, node_type,
                    node_id: str, count: int,
                    pin_args: str):
        # after adding node in canvas
        # first time make new model.
        id_string, inherit = self.db_link.get_args_id(node_name)
        model = ArgsEditableModel(
            db_link=self.db_link,
            node_name=node_name,
            node_type=node_type,
            node_id=id_string,
            inherit=inherit,
            pin_args=pin_args
            # if it's not 'None', then pin args will cover
            # the original args.
        )
        model.get_args(add_custom_args=True, count=count)
        # then store it but don't display it.
        self.edit_model[node_id] = model

    def delete_node(self, node_id: str):
        model = self.edit_model.get(node_id)
        # while remove the ref,
        # also remove the ref_by's relation.
        if model.node_name == 'PlaceHolder' or\
           model.node_type == 'Units':
            del model.ref_by
        # remove entire node item,
        # also remove the ref_to relation.
        else:
            for _, _, value_item in model.items():
                if hasattr(value_item, '_ref_to'):
                    src_node_id = value_item._ref_to_node_id
                    src_model = self.edit_model.get(src_node_id)
                    src_model.rb_semaphore.popup(node_id,
                                                 value_item.id_str)
        # finally clean it all.
        self.edit_model.__delitem__(node_id)
        self.setModel(self.null_model)

    def fetch_node(self, node_id: str):
        # get the arg model by id.
        return self.edit_model.get(node_id)

    # ------Operations on Ref Model------

    def delete_ref_related(self, src_model_id: str, dst_model_id: str):
        # while deleting ref edge will trigger this method only.
        # through ref_id will get the model of ref edge's start item.
        self.current_ref_model = self.edit_model.get(src_model_id)
        self.current_ref_dst_model_id = dst_model_id
        # if one start item connected with one node item.
        # under this situation, just del the ref_by.
        if self.current_ref_model.rb_semaphore.count(dst_model_id) == 1:
            self.current_ref_model.rb_semaphore.popup(dst_model_id, None)
            # single connected ref edge still needs these signals.
            self.REST_REF_ITEMS_COUNT.emit(0)
            self.WAS_DONE_PICKING_ONE.emit(True)
        # if one start item connected with one node but multi items.
        # then pop up a menu to decide which edge.
        else:
            fake_event = QContextMenuEvent(QContextMenuEvent.Mouse, QCursor.pos())
            self.contextMenuEvent(fake_event)

    def delete_rm_selected(self):
        # deleted the one item that selected in right menu.
        ref_item_id = self.sender().objectName()
        self.current_ref_model.rb_semaphore.popup(self.current_ref_dst_model_id, ref_item_id)
        # if one ref node has multi ref edges connected to one node,
        # view will only display one of the them.
        # so do not delete ref edge until there's no edge left.
        rest_ref_edge_count = self.current_ref_model.rb_semaphore.count(self.current_ref_dst_model_id)
        self.REST_REF_ITEMS_COUNT.emit(rest_ref_edge_count)
        self.WAS_DONE_PICKING_ONE.emit(True)

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

    # ------Operations on Model------

    def delete_io(self, src_model_id: str, dst_model_id: str):
        io_model = self.edit_model.get(dst_model_id)
        io_model.io_semaphore.popup(src_model_id)
