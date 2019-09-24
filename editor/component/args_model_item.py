from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QStandardItem, QColor

from cfg import color
from lib import type_color_map


class ArgNameItem(QStandardItem):

    def __init__(self, mode, tooltip, *args):
        # assign mode and tooltips first
        super().__init__(*args)

        if mode == 'inh':
            self.setBackground(QColor(color['INH_ARG']))
        else:
            self.setBackground(QColor(color['ORG_ARG']))

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

    def __init__(self, tooltip, *args):
        super().__init__(*args)
        self.is_changed = False

        self.setEditable(True)
        self.setToolTip(tooltip)

    def has_changed(self):
        self.is_changed = True
        self.setBackground(QColor(color['ARG_CHANGED']))


class ArgComboBox(QComboBox):

    def __init__(self, box_args: list, parent=None):
        super().__init__(parent)

        self.addItems(box_args)
        self.setMaxVisibleItems(7)
        self.setInsertPolicy(QComboBox.InsertAtBottom)
