from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

from editor.widgets.node_menu import KMBNodesMenu
from editor.graphic.node_view import KMBNodeGraphicView
from editor.wrapper.wrap_scene import KMBNodeScene
from editor.wrapper.wrap_args import KMBArgsMenu


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
        # set editing mode, now can add nodes.
        self.nodes_menu.clicked_tool_button_item.connect(
            self.nodes_view.set_editing_mode
        )
        # add new node and store it.
        self.nodes_view.add_new_node_item.connect(
            self.args_menu.panel.commit_node
        )
        # load selected node's args.
        self.nodes_view.selected_node_item.connect(
            self.args_menu.panel.set_editing_args
        )
        # ready to delete selected node.
        self.nodes_view.selected_delete_node.connect(
            self.args_menu.panel.delete_node
        )

    def serialize(self):
        self.node_scene.serialize()
        self.args_menu.serialize()
