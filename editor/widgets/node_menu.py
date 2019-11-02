import sqlite3

from PyQt5.QtWidgets import QVBoxLayout, QToolButton, QGroupBox, QToolBox, QTabWidget
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from cfg import icon, NODE_ICONx500_PATH


DATABASE = sqlite3.connect('lib/node.db')
CURSOR = DATABASE.cursor()


class KMBNodesMenu(QTabWidget):

    CLICKED_NODE_BUTTON_ITEM = pyqtSignal(str, str, str)  # name, category, sort

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
                node_button.setToolTip(tips)
                tool_icon_path = NODE_ICONx500_PATH.format(s, name)
                self.valid_node_button(node_button, name,
                                       tool_icon_path)
                # add clicked event handler
                node_button.clicked.connect(self.clicked_handler)
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
        pass

    def clicked_handler(self):
        clicked_item_name = self.sender().text()
        res = CURSOR.execute(f'SELECT CATEGORY, SORT '
                             f'FROM nodes '
                             f'WHERE NAME="{clicked_item_name}"').fetchone()
        self.CLICKED_NODE_BUTTON_ITEM.emit(clicked_item_name, res[0], res[1])

    @classmethod
    def valid_node_button(cls,
                          node_button: QToolButton,
                          text: str,
                          icon_path: str,
                          icon_size=50):

        node_button.setText(text)
        node_button.setIcon(QIcon(icon_path))
        node_button.setIconSize(QSize(icon_size, icon_size))
        node_button.setAutoRaise(True)
        node_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
