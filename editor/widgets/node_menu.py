import sqlite3

from PyQt5.QtWidgets import QVBoxLayout, QToolButton, QGroupBox, QToolBox, QTabWidget
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lib import read_custom_pin, create_ucp_tip
from cfg import icon, NODE_ICONx500_PATH


DATABASE = sqlite3.connect('lib/node.db')
CURSOR = DATABASE.cursor()


class KMBNodesMenu(QTabWidget):

    # name, category, sort
    CLICKED_NODE_BUTTON_ITEM = pyqtSignal(str, str, str)
    # name, category, sort, args
    CLICKED_PIN_BUTTON_ITEM = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layer_nodes = QToolBox(self)
        self.common_nodes = QToolBox(self)
        self.units_nodes = QToolBox(self)
        # custom pin tab
        self.pin_nodes = QToolBox(self)

        self.set_toolbox()
        self.addTab(self.pin_nodes, "Pins")
        self.addTab(self.layer_nodes, "Layers")
        self.addTab(self.common_nodes, "Common")
        self.addTab(self.units_nodes, "Units")

        self.setTabIcon(0, QIcon(icon['PIN']))
        self.setCurrentWidget(self.layer_nodes)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        self.tabBarClicked.connect(self.set_pin_box)

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
                self.valid_node_button(node_button, name, tips,
                                       NODE_ICONx500_PATH.format(s, name))
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

    def set_pin_box(self, tab_idx: int):
        """ Every time click this tab will get refresh. """
        if tab_idx != 0:
            return
        pins = read_custom_pin()
        if pins is None:
            return

        # avoid repeating group box.
        self.pin_nodes.removeItem(0)
        pin_box = QGroupBox(self)
        pin_layout = QVBoxLayout(pin_box)
        pin_layout.setAlignment(Qt.AlignTop)
        for pin in pins:
            id_, pin_name, pin_args, category, org_name, org_sort = pin
            pin_button = QToolButton(self)
            self.valid_node_button(pin_button, pin_name,
                                   create_ucp_tip(pin),
                                   NODE_ICONx500_PATH.format('Core', org_name),
                                   text_button_beside=False)
            pin_button.setObjectName(f'{pin_args}-{org_name}-{org_sort}')
            pin_button.clicked.connect(self.pin_box_clicked_handler)
            pin_layout.addWidget(pin_button, alignment=Qt.AlignLeft)
        self.pin_nodes.addItem(pin_box, '')

    def tool_box_clicked_handler(self):
        clicked_item_name = self.sender().text()
        res = CURSOR.execute(f'SELECT CATEGORY, SORT '
                             f'FROM nodes '
                             f'WHERE NAME="{clicked_item_name}"').fetchone()
        self.CLICKED_NODE_BUTTON_ITEM.emit(clicked_item_name, res[0], res[1])

    def pin_box_clicked_handler(self):
        clicked_pin = self.sender()
        pin = clicked_pin.objectName().split('-')

    @classmethod
    def valid_node_button(cls,
                          node_button: QToolButton,
                          text: str,
                          tooltip: str,
                          icon_path: str,
                          icon_size=50,
                          text_button_beside=True):

        node_button.setText(text)
        node_button.setIcon(QIcon(icon_path))
        node_button.setIconSize(QSize(icon_size, icon_size))
        node_button.setToolTip(tooltip)
        node_button.setAutoRaise(True)
        if text_button_beside:
            node_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        else:
            node_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
