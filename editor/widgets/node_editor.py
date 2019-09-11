from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

from editor.widgets import KMBNodesMenu, KMBNodesArgsMenu


class MainNodeEditor(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # init UI
        self.nodes_menu = KMBNodesMenu(self)
        self.nodes_args = KMBNodesArgsMenu(self)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 2)
        self.setLayout(self.layout)

        self.layout.addWidget(self.nodes_menu, alignment=Qt.AlignLeft)
        self.layout.addWidget(self.nodes_args, alignment=Qt.AlignRight)

        # loading node's args
        self.nodes_menu.clicked_tool_button_item.connect(
            self.nodes_args.load_args_by_name)
