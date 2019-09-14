import sqlite3

from PyQt5.QtWidgets import (QVBoxLayout, QToolButton, QGroupBox, QToolBox,
                             QTabWidget)
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon


DATABASE = sqlite3.connect('lib/node.db')
CURSOR = DATABASE.cursor()

NODE_ICON_PATH = 'lib/icon/nodesx500/{}.png'


class KMBNodesMenu(QTabWidget):

    clicked_tool_button_item = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layer_tool = QToolBox(self)
        self.other_tool = QToolBox(self)

        self.set_toolbox()
        self.addTab(self.layer_tool, "Layers")
        self.addTab(self.other_tool, "Other")
        self.setFixedWidth(250)

    def set_toolbox(self):
        nodes = {}
        res = CURSOR.execute('SELECT * FROM nodes')
        for one in res.fetchall():
            _, name, info, _, _, sort, category = one
            nodes.setdefault((sort, category), []).append((name, info))

        for sc, ls in nodes.items():
            s, c = sc
            group_box = QGroupBox(self)
            vb_layout = QVBoxLayout(group_box)
            vb_layout.setAlignment(Qt.AlignTop)
            for nm, io in ls:
                # init tool button
                tool_button = QToolButton(self)
                tool_button.setToolTip(io)
                tool_icon_path = NODE_ICON_PATH.format(nm.lower())
                self.valid_tool_button(tool_button, nm,
                                       tool_icon_path)
                # add clicked event handler
                tool_button.clicked.connect(self.clicked_tool_button_handler)
                # add it in layout
                vb_layout.addWidget(tool_button, alignment=Qt.AlignLeft)
            if c.lower() == 'layers':
                self.layer_tool.addItem(group_box, s)
            else:
                self.other_tool.addItem(group_box, s)

    def clicked_tool_button_handler(self):
        clicked_item_name = self.sender().text()
        self.clicked_tool_button_item.emit(clicked_item_name)

    @classmethod
    def valid_tool_button(cls,
                          tool_button: QToolButton,
                          text: str,
                          icon_path: str,
                          icon_size=50):

        tool_button.setText(text)
        tool_button.setIcon(QIcon(icon_path))
        tool_button.setIconSize(QSize(icon_size, icon_size))
        tool_button.setAutoRaise(True)
        tool_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
