import sqlite3

from PyQt5.QtWidgets import (QVBoxLayout, QToolButton, QGroupBox,
                             QToolBox, QTabWidget, QGridLayout)
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from editor.component.pin_toolbutton import PinToolBox
from lib import read_custom_pin, create_ucp_tip
from cfg import icon, NODE_ICONx500_PATH


DATABASE = sqlite3.connect('lib/node.db')
CURSOR = DATABASE.cursor()


class KMBNodesMenu(QTabWidget):

    # name, category, sort
    CLICKED_NODE_BUTTON_ITEM = pyqtSignal(str, str, str)
    # org_name, org_category, org_sort, pin_args, pin_id
    CLICKED_PIN_BUTTON_ITEM = pyqtSignal(str, str, str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layer_nodes = QToolBox(self)
        self.common_nodes = QToolBox(self)
        self.units_nodes = QToolBox(self)
        # custom pin tab
        self.pin_nodes = QToolBox(self)

        self.set_toolbox()
        self.set_pin_box()
        self.addTab(self.pin_nodes, "Pins")
        self.addTab(self.layer_nodes, "Layers")
        self.addTab(self.common_nodes, "Common")
        self.addTab(self.units_nodes, "Units")

        self.setTabIcon(0, QIcon(icon['PIN_TAB']))
        self.setCurrentWidget(self.layer_nodes)
        self.setMinimumWidth(290)
        self.setMaximumWidth(500)

    def set_toolbox(self):
        nodes = {}
        res = CURSOR.execute('SELECT * FROM nodes')
        for one in res.fetchall():
            _, name, info, _, _, sort, category = one
            nodes.setdefault((sort, category), []).append((name, info))

        for sc, ls in nodes.items():
            s, c = sc  # sorts & category
            group_box = QGroupBox(self)
            vb_layout = QVBoxLayout(group_box)
            vb_layout.setAlignment(Qt.AlignTop)
            for name, tips in ls:
                # init tool button
                node_button = QToolButton(self)
                self.set_node_button(node_button,
                                     text=name,
                                     tooltip=tips,
                                     icon_path=NODE_ICONx500_PATH.format(s, name),
                                     signal=f'{name}-{c}-{s}')
                # add clicked event handler
                node_button.clicked.connect(self.tool_box_clicked_handler)
                # add it in layout
                vb_layout.addWidget(node_button, alignment=Qt.AlignLeft)
            if c.lower() == 'layers':
                self.layer_nodes.addItem(group_box, s)
            elif c.lower() == 'units':
                self.units_nodes.addItem(group_box, s)
            elif c.lower() == 'common':
                self.common_nodes.addItem(group_box, s)
            # else:

    def set_pin_box(self):
        """ Click refresh button will get refresh. """
        pins = read_custom_pin()
        if pins is None:
            return

        pin_box = QGroupBox(self)
        pin_layout = QGridLayout(pin_box)
        pin_layout.setAlignment(Qt.AlignTop)
        col = 4

        # add refresh button first.
        refresh = QToolButton(self)
        self.set_node_button(refresh,
                             text='Refresh',
                             tooltip='Refresh the Pins panel.',
                             icon_path=icon['REFRESH'],
                             icon_size=20,
                             text_button_beside=False)
        refresh.clicked.connect(self.refresh_clicked_handler)
        # refresh take out first coord.
        coords = self.get_grid_pos(0, col)
        pin_layout.addWidget(refresh, *coords)

        # then add other pin buttons.
        for i, pin in enumerate(pins, start=1):
            id_, pin_name, pin_args, category, org_name = pin
            org_category, org_sort = self.get_cs_from_db(org_name)
            pin_button = PinToolBox(self,
                                    text=pin_name,
                                    tooltip=create_ucp_tip(pin),
                                    icon_path=NODE_ICONx500_PATH.format(org_sort, org_name),
                                    icon_size=50,
                                    signal=f'{org_name}-{org_category}-{org_sort}-{pin_args}-{id_}',
                                    refresh_button=refresh)
            pin_button.clicked.connect(self.pin_box_clicked_handler)
            pos = self.get_grid_pos(i, col)
            pin_layout.addWidget(pin_button, *pos)
        self.pin_nodes.addItem(pin_box, 'Customize Pins')

    def tool_box_clicked_handler(self):
        clicked_node = self.sender()
        node = clicked_node.objectName().split('-')
        self.CLICKED_NODE_BUTTON_ITEM.emit(*node)

    def pin_box_clicked_handler(self):
        clicked_pin = self.sender()
        pin = clicked_pin.objectName().split('-')
        self.CLICKED_PIN_BUTTON_ITEM.emit(*pin)

    def refresh_clicked_handler(self):
        self.pin_nodes.removeItem(0)
        self.set_pin_box()

    # ----------UTILS----------

    @classmethod
    def get_grid_pos(cls, n: int, col: int):
        # get coord by col.
        x = n // col
        y = n % col
        return x, y

    @classmethod
    def get_cs_from_db(cls, node_name: str):
        # get category and sort from database by node name.
        res = CURSOR.execute('SELECT CATEGORY, SORT '
                             'FROM nodes '
                             'WHERE NAME=(?)', (node_name,)).fetchone()
        return res

    @classmethod
    def set_node_button(cls,
                        node_button: QToolButton,
                        text: str,
                        tooltip: str,
                        icon_path: str,
                        icon_size=50,
                        text_button_beside=True,
                        signal: str = None):

        node_button.setText(text)
        node_button.setIcon(QIcon(icon_path))
        node_button.setIconSize(QSize(icon_size, icon_size))
        node_button.setToolTip(tooltip)
        node_button.setAutoRaise(True)
        if text_button_beside:
            node_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        else:
            node_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # use objectName as transmission medium.
        if signal is not None:
            node_button.setObjectName(signal)
