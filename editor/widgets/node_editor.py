import ctypes

from PyQt5.QtWidgets import QWidget, QSplitter
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
        self.nodes_scene = KMBNodeScene(self)
        self.nodes_view = KMBNodeGraphicView(
            self.nodes_scene.graphic_scene,
            parent.statusBar().showMessage,
            self)
        self.splitter = QSplitter(self)
        # setup
        self.setup_layout()
        self.setup_slots()

    # ----------SETUP----------

    def setup_layout(self):
        self.splitter.addWidget(self.nodes_menu)
        self.splitter.addWidget(self.nodes_view)
        self.splitter.addWidget(self.args_menu.panel)
        self.splitter.setOrientation(Qt.Horizontal)

    def setup_slots(self):
        # preview node's args.
        self.nodes_menu.clicked_node_button_item.connect(
            self.args_menu.panel.set_preview_args
        )
        # set editing mode, now can add nodes.
        self.nodes_menu.clicked_node_button_item.connect(
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
        # ready to pop up the right menu of node.
        self.nodes_view.pop_up_right_menu.connect(
            self.send_args_to_node
        )
        # after picking up an arg item from right menu
        self.nodes_scene.graphic_scene.picked_one_arg_to_ref.connect(
            self.args_menu.panel.modify_ref
        )
        # after not picking up an arg item from right menu
        self.nodes_scene.graphic_scene.do_not_pick_one.connect(
            self.nodes_view.set_chosen_state_from_rm
        )

    # ----------FUNCTIONS----------

    def send_args_to_node(self, dst_node_id: str):
        fetched_dst_model = self.args_menu.fetch(dst_node_id)
        # get the node by id (a very unsafe way)
        dst_gr_node = ctypes.cast(int(dst_node_id), ctypes.py_object).value
        # pass the args to node,
        # now is able to show them on right menu.
        dst_gr_node.feed_args(fetched_dst_model)

    def serialize(self):
        # organize the nodes here
        # fill with node's <var> and <args> tag
        nodes = self.nodes_scene.serialize()
        args, vars = self.args_menu.serialize()
        for node_id in nodes.keys():
            nodes[node_id]['var'] = vars.get(node_id)
            nodes[node_id]['args'] = args.get(node_id)

        for k, v in nodes.items():
            print(k, v)
        return nodes

    def deserialize(self):
        pass
