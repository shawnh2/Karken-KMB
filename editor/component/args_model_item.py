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

    def __init__(self,
                 value, dtype,
                 belong_to:str,
                 tag=0, store_bg=False):
        # save the initial value of one arg
        self._init_value = value
        self._value = value
        self._store_bg = store_bg
        self.belong_to = belong_to
        # store all items that has been referenced.
        self._ref_by_list = []
        # behind the widgets is self
        if self._store_bg:
            super().__init__()
        else:
            super().__init__(self._value)
        self.is_changed = False
        self.is_referenced = False
        self.dtype = dtype
        # default tag is 0.
        # when self is token by other widget,
        # 1 is checkbox, 2 is combobox.
        self.tag = tag
        # color for plain, changed & referenced
        self.pln_color = QColor(color['ARG_NORMAL'])
        self.chg_color = QColor(color['ARG_CHANGED'])
        self.ref_color = QColor(color['ARG_REFED'])

        self.setEditable(True)
        self.setToolTip(dtype)

    def __repr__(self):
        return f"<Arg-TAG:{self.tag}-ARG:{self.belong_to}>"

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

    def set_ref_to(self, ref_to):
        self._ref_to = ref_to
        self.setText(self._ref_to.text())
        # set referenced bg color,
        # undo all is_changed sign here.
        self.is_changed = False
        self.is_referenced = True
        self.setBackground(self.ref_color)

    def get_ref_to(self):
        return str(id(self._ref_to))

    def del_ref_to(self):
        del self._ref_to
        # after deleting, everything back to normal.
        # arg value becomes initial value.
        self.is_changed = False
        self.is_referenced = False
        self.setText(self._init_value)
        self.setBackground(self.pln_color)

    ref_to = property(get_ref_to, set_ref_to, del_ref_to)

    @property
    def var_name(self):
        if hasattr(self, '_ref_to'):
            return self._ref_to.text()
        else:
            return self.text()

    def text(self):
        if self._store_bg:
            return self._value
        else:
            return super().text()

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
