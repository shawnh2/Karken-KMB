from PyQt5.QtWidgets import QComboBox, QCheckBox
from PyQt5.QtGui import QStandardItem, QColor, QIcon

from cfg import color, icon
from lib import type_color_map


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

    def __init__(self, value, dtype, tag=0, store_bg=False):
        self._value = value
        self._store_bg = store_bg
        if self._store_bg:
            super().__init__()
        else:
            super().__init__(self._value)
        self.is_changed = False
        self.is_referenced = False
        self.dtype = dtype
        # default tag is 0.
        # when self is token by other widget,
        # 1 means checkbox, 2 means combobox.
        self.tag = tag

        self.setEditable(True)
        self.setToolTip(dtype)

    def has_changed(self):
        self.is_changed = True
        # only set changed color for normal edit item
        if self.tag == 0:
            self.setBackground(QColor(color['ARG_CHANGED']))

    def has_referenced(self):
        self.is_referenced = True
        if self.tag == 0:
            self.setBackground(QColor(color['ARG_REFED']))

    def text(self):
        return self._value

    def setText(self, p_str):
        if self._store_bg:
            self._value = p_str
        else:
            super().setText(p_str)


class ArgComboBox(QComboBox):

    def __init__(self, box_args: list, default: str, at: int, parent=None):
        super().__init__(parent)
        self.at = at  # index at model

        self.addItems(box_args)
        self.setCurrentText(default)
        self.setItemIcon(box_args.index(default), QIcon(icon["COMBO"]))
        self.setMaxVisibleItems(7)
        self.setInsertPolicy(QComboBox.InsertAtBottom)


class ArgCheckBox(QCheckBox):

    def __init__(self, arg_init, at: int):
        super().__init__(arg_init)
        self.at = at  # index at model
        if arg_init == "True":
            self.setChecked(True)
        else:
            self.setChecked(False)
