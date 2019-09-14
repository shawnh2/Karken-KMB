from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

from editor.widgets import KMBNodesMenu, KMBNodeGraphicView
from editor.core import KMBNodeScene, KMBArgsMenu


class MainNodeEditor(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # init UI
        self.nodes_menu = KMBNodesMenu(self)
        self.args_menu = KMBArgsMenu(self)
        self.node_scene = KMBNodeScene()
        self.nodes_view = KMBNodeGraphicView(self.node_scene.graphic_scene,
                                             parent.statusBar().showMessage,
                                             self)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.layout)

        self.layout.addWidget(self.nodes_menu, alignment=Qt.AlignLeft)
        self.layout.addWidget(self.nodes_view)
        self.layout.addWidget(self.args_menu.panel, alignment=Qt.AlignRight)

        # preview node's args.
        self.nodes_menu.clicked_tool_button_item.connect(
            self.args_menu.panel.set_preview_args
        )
        # add the token node to mouse.
        self.nodes_menu.clicked_tool_button_item.connect(
            self.nodes_view.set_editing_mode
        )
        # load selected node's args.
        self.nodes_view.selected_node_item.connect(
            self.args_menu.panel.set_editing_args
        )
