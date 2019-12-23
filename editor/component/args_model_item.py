from PyQt5.QtWidgets import (QComboBox, QCheckBox, QListView, QPushButton,
                             QDialog, QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout)
from PyQt5.QtGui import QStandardItem, QColor, QIcon
from PyQt5.QtCore import Qt

from cfg import color, icon, SS_ARGBOX
from lib import type_color_map, load_stylesheet
from editor.component.mini_button import MiniSquareButton


class ArgNameItem(QStandardItem):

    def __init__(self, mode, tooltip, *args):
        # assign mode and tooltips first
        super().__init__(*args)

        self.mode = mode
        if self.mode == 'inh':
            self.setBackground(QColor(color['INH_ARG']))
        elif self.mode == 'org':
            self.setBackground(QColor(color['ORG_ARG']))
        else:  # 'var'
            self.setBackground(QColor(color['CUS_ARG']))

        self.setEditable(False)
        self.setToolTip(tooltip)


class ArgTypeItem(QStandardItem):

    def __init__(self, args):
        self.type_string = args
        self.type_color, self.raw_type_name = \
            type_color_map(self.type_string)

        super().__init__(self.raw_type_name)

        self.setBackground(QColor(self.type_color))
        self.setEditable(False)


class ArgEditItem(QStandardItem):

    def __init__(self,
                 value,
                 dtype,
                 belong_to: str,
                 tag: int = 0,
                 store_bg: bool = False,
                 is_pined: bool = False,
                 is_required: bool = False):
        # save the initial value of one arg
        self._init_value = value if value else ''
        self._value = value
        self._store_bg = store_bg
        self.dtype = dtype
        # this arg value item belongs to ...
        self.belong_to = belong_to
        # behind the widgets is self
        if self._store_bg:
            super().__init__()
        else:
            super().__init__(self._value)
        # default tag is 0.
        # when self is token by other widget,
        # 1 is checkbox, 2 is combobox, 3 is io-order.
        self.tag = tag

        self.is_changed = False
        self.is_referenced = False
        self.is_pined = is_pined
        self.is_required = is_required
        # color for plain, changed & referenced.
        self.pln_color = QColor(color['ARG_NORMAL'])
        self.chg_color = QColor(color['ARG_CHANGED'])
        self.ref_color = QColor(color['ARG_REFED'])

        self.setEditable(True)
        self.setToolTip(self.dtype)

    def __repr__(self):
        return f"<ArgEditItem ARG:{self.belong_to} at {str(id(self))[-4:]}>"

    @property
    def var_name(self):
        if hasattr(self, '_ref_to'):
            return self._ref_to.text()

    @property
    def id_str(self):
        return str(id(self))

    # ------REF TO------
    # This semaphore is maintained by self.

    def set_ref_to(self, ref_to):
        (self._ref_to_node_id,
         self._ref_to) = ref_to
        # ref value has prefix '@'
        self.value = '@' + self._ref_to.value
        # set referenced bg color,
        # undo all is_changed sign here.
        self.is_changed = False
        self.is_referenced = True
        if self.tag == 0:
            self.setBackground(self.ref_color)
        # ref value cannot be changed unless remove it.
        self.setEditable(False)

    def get_ref_to(self):
        return self._ref_to_node_id

    def del_ref_to(self):
        # be called while deleting ref src node.
        del self._ref_to
        # after deleting, everything back to normal.
        # arg value becomes initial value.
        self.is_changed = False
        self.is_referenced = False
        self.value = self._init_value
        self.setBackground(self.pln_color)
        self.setEditable(True)

    ref_to = property(get_ref_to, set_ref_to, del_ref_to)

    def set_value(self, value: str):
        """ A proxy of setText() with value check. """
        self._value = value
        if not self._store_bg:
            self.setText(self._value)

    def get_value(self):
        # whether store in bg or not, will get the value anyway.
        # text() will only get the front value, not the one
        # that store in background.
        return self._value

    value = property(get_value, set_value)

    def check_changed(self, value: str) -> bool:
        # if after all, value still equal to initial value,
        # then consider this to be unchanged.
        return self._init_value != value

    def has_changed(self):
        self.is_changed = True
        # only set changed color for normal edit item
        if self.tag == 0:
            self.setBackground(self.chg_color)

    def undo_change(self):
        self.is_changed = False
        self.setBackground(self.pln_color)


class ArgComboBox(QComboBox):

    def __init__(self,
                 box_args: list,
                 default: str,
                 at: int,
                 parent=None):
        super().__init__(parent)
        self.at = at  # index at model
        self.box_args = box_args
        self.n = len(self.box_args)

        self.addItems(self.box_args)
        self.setCurrentText(default)
        self.setStyleSheet(load_stylesheet(SS_ARGBOX))
        # set icon for all items.
        init_idx = self.box_args.index(default)
        for idx in range(len(self.box_args)):
            if init_idx == idx:
                self.setItemIcon(idx, QIcon(icon["COMBO"]))
            else:
                self.setItemIcon(idx, QIcon(icon['COMBO_EMPTY']))
        self.setMaxVisibleItems(8)
        self.setInsertPolicy(QComboBox.InsertAtBottom)
        self.setView(QListView())  # set style later.

    def set_reference(self):
        # set item type is reference.
        self.setEnabled(False)
        self.setItemIcon(self.n-1, QIcon(icon['COMBO_REF']))


class ArgCheckBox(QCheckBox):

    def __init__(self, arg_init, at: int):
        super().__init__(arg_init)
        self.at = at  # index at model
        if arg_init == "True":
            self.setChecked(True)
        else:
            self.setChecked(False)


class ArgIOOrderButton(QPushButton):
    """ Active in Model node input and output items.
    Show up a list panel by clicking it, and can change
    the order of input or output items inside panel. """

    def __init__(self, name: str, at: int, model_id: str):
        self.title = f'{name.capitalize()} Panel'
        super().__init__(self.title)
        self.at = at  # index in model
        self.io_type = name[0]
        self.model_id = model_id
        # init panel
        self.io_panel = _ArgIOOrderPanel(self)

    def show_panel(self, io_semaphore):
        assert self.io_type in ('i', 'o')
        if self.io_type == 'i':
            res = self.io_panel(io_semaphore[0])
        else:
            res = self.io_panel(io_semaphore[1])
        return res


class _ArgIOOrderPanelListItem(QListWidgetItem):
    """ Override list widget item. """

    def __init__(self, text: str, key: str):
        super().__init__(text)
        self.key = key


class _ArgIOOrderPanel(QDialog):
    """ The panel of I/O order list. """

    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(320, 280)
        self.setWindowTitle(parent.title)
        # init widgets
        self.order_list = QListWidget(self)
        self.order_list.setAlternatingRowColors(True)
        # init buttons
        self.btn_up = MiniSquareButton(icon=icon['MINI_UP'])
        self.btn_down = MiniSquareButton(icon=icon['MINI_DOWN'])
        self.btn_cancel = MiniSquareButton(icon=icon['MINI_CANCEL'])
        self.btn_confirm = MiniSquareButton(icon=icon['MINI_CONFIRM'])
        # buttons layout
        self.btn1_layout = QVBoxLayout()
        self.btn1_layout.addWidget(self.btn_up, alignment=Qt.AlignTop)
        self.btn1_layout.addWidget(self.btn_down, alignment=Qt.AlignTop)
        self.btn1_layout.addStretch(1)
        self.btn2_layout = QVBoxLayout()
        self.btn2_layout.addWidget(self.btn_cancel, alignment=Qt.AlignBottom)
        self.btn2_layout.addWidget(self.btn_confirm, alignment=Qt.AlignBottom)
        self.btn2_layout.addStretch(1)
        self.btn_layout = QVBoxLayout()
        self.btn_layout.addLayout(self.btn1_layout)
        self.btn_layout.addLayout(self.btn2_layout)
        # main layout
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.order_list, alignment=Qt.AlignLeft)
        self.layout.addLayout(self.btn_layout)
        # init slots
        self.btn_up.clicked.connect(self._up_pressed_handler)
        self.btn_down.clicked.connect(self._down_pressed_handler)
        self.btn_cancel.clicked.connect(self._cancel_pressed_handler)
        self.btn_confirm.clicked.connect(self._confirm_pressed_handler)
        # temp
        self.semaphore: dict = None
        self.result: list = None

    def __call__(self, semaphore: dict):
        self.semaphore = semaphore
        self.initialize_semaphore()
        self.exec()
        return self.result

    def initialize_semaphore(self):
        # load items into list widget.
        self.order_list.clear()
        for key, vn_item in self.semaphore.items():
            self.order_list.addItem(
                _ArgIOOrderPanelListItem(vn_item.value, key=key)
            )

    def _up_pressed_handler(self):
        # selected or first item
        idx = self.order_list.currentRow()
        if idx > 0:
            item = self.order_list.takeItem(idx)
            self.order_list.insertItem(idx - 1, item)
            del item

    def _down_pressed_handler(self):
        idx = self.order_list.currentRow()
        if idx < self.order_list.count() - 1:
            item = self.order_list.takeItem(idx)
            self.order_list.insertItem(idx + 1, item)
            del item

    def _cancel_pressed_handler(self):
        # close and recover
        self.close()
        self.initialize_semaphore()
        self.semaphore = None
        self.result = None

    def _confirm_pressed_handler(self):
        # close and accept changes
        self.close()
        new_keys = []
        for row in range(self.order_list.count()):
            item = self.order_list.item(row)
            new_keys.append(item.key)
        self.result = new_keys
        self.semaphore = None
