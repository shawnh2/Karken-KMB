import sqlite3

from PyQt5.QtWidgets import QVBoxLayout, QToolButton, QGroupBox, QToolBox, QTabWidget
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from cfg import NODE_ICONx500_PATH


DATABASE = sqlite3.connect('lib/node.db')
CURSOR = DATABASE.cursor()


class KMBNodesMenu(QTabWidget):

    clicked_node_button_item = pyqtSignal(str, str)  # name & category

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layer_nodes = QToolBox(self)
        self.other_nodes = QToolBox(self)
        self.common_nodes = QToolBox(self)

        self.set_toolbox()
        self.addTab(self.layer_nodes, "Layers")
        self.addTab(self.common_nodes, "Common")
        self.addTab(self.other_nodes, "Other")
        self.setMinimumWidth(270)

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
                tool_icon_path = NODE_ICONx500_PATH.format(name)
                self.valid_node_button(node_button, name,
                                       tool_icon_path)
                # add clicked event handler
                node_button.clicked.connect(self.clicked_handler)
                # add it in layout
                vb_layout.addWidget(node_button, alignment=Qt.AlignLeft)
            if c.lower() == 'layers':
                self.layer_nodes.addItem(group_box, s)
            elif c.lower() == 'other':
                self.other_nodes.addItem(group_box, s)
            elif c.lower() == 'common':
                self.common_nodes.addItem(group_box, s)
            # else:

    def clicked_handler(self):
        clicked_item_name = self.sender().text()
        category = CURSOR.execute(f'SELECT CATEGORY '
                                  f'FROM nodes '
                                  f'WHERE NAME="{clicked_item_name}"').fetchone()
        self.clicked_node_button_item.emit(clicked_item_name, category[0])

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
