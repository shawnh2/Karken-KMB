import ctypes

from PyQt5.QtWidgets import QWidget, QSplitter
from PyQt5.QtCore import Qt

from editor.widgets.node_menu import KMBNodesMenu
from editor.graphic.node_view import KMBNodeGraphicView
from editor.wrapper.wrap_scene import KMBNodeScene
from editor.wrapper.wrap_args import KMBArgsMenu
from cfg import DEBUG


class MainNodeEditor(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # init UI
        self.nodes_scene = KMBNodeScene(self)
        self.nodes_view = KMBNodeGraphicView(
            self.nodes_scene.graphic_scene,
            parent.statusBar().showMessage, self
        )
        self.nodes_menu = KMBNodesMenu(self)
        self.args_menu = KMBArgsMenu(self)
        self.splitter = QSplitter(self)
        self.history = self.nodes_scene.history
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
        # +++++++++++++++++++++++++++++++++++
        #           FROM NODE-MENU
        # +++++++++++++++++++++++++++++++++++
        # preview node's args.
        self.nodes_menu.CLICKED_NODE_BUTTON_ITEM.connect(
            self.args_menu.panel.set_preview_args
        )
        # set editing mode, now can add nodes.
        self.nodes_menu.CLICKED_NODE_BUTTON_ITEM.connect(
            self.nodes_view.set_editing_mode
        )
        # do the same things.
        self.nodes_menu.CLICKED_PIN_BUTTON_ITEM.connect(
            self.args_menu.panel.set_preview_args
        )
        self.nodes_menu.CLICKED_PIN_BUTTON_ITEM.connect(
            self.nodes_view.set_editing_mode
        )

        # +++++++++++++++++++++++++++++++++++
        #             FROM VIEW
        # +++++++++++++++++++++++++++++++++++
        # add new node and store it.
        self.nodes_view.ADD_NEW_NODE_ITEM.connect(
            self.args_menu.panel.commit_node
        )
        # load selected node's args.
        self.nodes_view.SELECTED_NODE_ITEM.connect(
            self.args_menu.panel.set_editing_args
        )
        # ready to delete selected node.
        self.nodes_view.SELECTED_DELETE_NODE.connect(
            self.args_menu.panel.delete_node
        )
        # ready to delete ref related items.
        self.nodes_view.DEL_REF_RELATED_ITEMS.connect(
            self.args_menu.panel.delete_ref_related
        )
        # ready to delete io item.
        self.nodes_view.DEL_IO_EDGE_ITEM.connect(
            self.args_menu.panel.delete_io
        )
        # ready to pop up the right menu of node.
        self.nodes_view.POP_UP_RIGHT_MENU.connect(
            self.send_args_to_node
        )
        # update x,y pos label.
        self.nodes_view.SCENE_POS_CHANGED.connect(
            self.send_pos_change_to_main
        )
        # has been modified.
        self.nodes_view.IS_MODIFIED.connect(
            self.send_modify_state_to_main
        )

        # +++++++++++++++++++++++++++++++++++
        #            FROM ARG-MENU
        # +++++++++++++++++++++++++++++++++++
        # sending the rest items count of ref dst node.
        self.args_menu.panel.REST_REF_ITEMS_COUNT.connect(
            self.nodes_view.set_rest_ref_dst_items_count
        )
        # do not pick one item to del.
        self.args_menu.panel.WAS_DONE_PICKING_ONE.connect(
            self.nodes_view.set_chosen_to_del_from_rm
        )
        # has been modified.
        self.args_menu.panel.IS_MODIFIED.connect(
            self.send_modify_state_to_main
        )

        # +++++++++++++++++++++++++++++++++++
        #            FROM SCENE
        # +++++++++++++++++++++++++++++++++++
        # after picking up an arg item from right menu.
        self.nodes_scene.graphic_scene.PICKED_ONE_ARG_TO_REF.connect(
            self.args_menu.panel.modify_ref
        )
        self.nodes_scene.graphic_scene.PICKED_ONE_TO_IO.connect(
            self.args_menu.panel.modify_io
        )
        # after not picking up an arg item from right menu.
        self.nodes_scene.graphic_scene.WAS_DONE_PICKING_ONE.connect(
            self.nodes_view.set_chosen_item_from_rm
        )

    # ----------FUNCTIONS----------

    def send_args_to_node(self, dst_node_id: str):
        fetched_dst_model = self.args_menu.fetch(dst_node_id)
        # get the node by id (a very unsafe way).
        dst_gr_node = ctypes.cast(int(dst_node_id), ctypes.py_object).value
        # pass the args to node,
        # now is able to show them on right menu.
        dst_gr_node.feed_args(fetched_dst_model)

    def send_pos_change_to_main(self, x, y):
        # send to main, display the real time xy pos.
        self.parent().update_xy_pos(x, y)

    def send_modify_state_to_main(self):
        # modify signals may come from any widget,
        # but finally go into main editor.
        self.parent().update_modify_state()

    def serialize(self):
        # call by Saving thread.
        # organize the nodes here,
        nodes_dict = self.nodes_scene.serialize()
        args_dict, vars_dict = self.args_menu.serialize()

        for node_id, cur_node in nodes_dict.items():
            # fill with node's <var> and <args> tag.
            cur_node['var'] = vars_dict.get(node_id)
            cur_args = args_dict.get(node_id)
            if cur_node.__contains__('args'):
                cur_node['args'] = cur_args
            # config the node's <mode>, especially for 'CA'.
            if cur_node['tag'] == 'layer' and \
               cur_node['mode'] == 'AC':
                ca = cur_args.get('layer')
                if ca[0]:
                    dst = nodes_dict[ca[0]].get('mode')
                    if dst:
                        nodes_dict[ca[0]]['mode'] = 'CA'
                    # if got no CA layer, it must be a ph.
                    # then set AC back to IO.
                    else:
                        cur_node['mode'] = 'IO'

        if DEBUG:
            for k, v in nodes_dict.items():
                print(v)
        return nodes_dict

    def deserialize(self, feeds: dict):
        # call by Loading thread.
        print(feeds)
        self.nodes_scene.deserialize(feeds, self.args_menu)
