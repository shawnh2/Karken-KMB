from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QStandardItem, QColor, QIcon

from cfg import color, icon
from lib import type_color_map


class ArgNameItem(QStandardItem):

    def __init__(self, mode, tooltip, *args):
        # assign mode and tooltips first
        super().__init__(*args)

        if mode == 'inh':
            self.setBackground(QColor(color['INH_ARG']))
        elif mode == 'org':
            self.setBackground(QColor(color['ORG_ARG']))
        else:
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

    def __init__(self, dtype, *args):
        super().__init__(*args)
        self.is_changed = False
        self.dtype = dtype
        self.tag = 0

        self.setEditable(True)
        self.setToolTip(dtype)

    def has_changed(self):
        self.is_changed = True
        self.setBackground(QColor(color['ARG_CHANGED']))

class ArgMarkItem(QStandardItem):
    """ The container of item which is other widget. """

    def __init__(self, tag, *args):
        super().__init__(*args)
        self.tag = tag
        self.dtype = 'Reference'
        self.setEditable(False)
        self.setEnabled(False)


class ArgComboBox(QComboBox):

    def __init__(self, box_args: list, default: str, parent=None):
        super().__init__(parent)

        self.addItems(box_args)
        self.setCurrentText(default)
        self.setItemIcon(box_args.index(default), QIcon(icon["COMBO"]))
        self.setMaxVisibleItems(7)
        self.setInsertPolicy(QComboBox.InsertAtBottom)
