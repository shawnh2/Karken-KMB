from editor.graphic.node_scene import KMBNodeGraphicScene
from editor.graphic.node_note import KMBNote
from editor.wrapper.wrap_edge import KMBEdge
from editor.wrapper.wrap_item import KMBNodeItem
from editor.wrapper.wrap_args import KMBArgsMenu
from editor.wrapper.serializable import Serializable
from editor.component.commands_stack import KMBHistoryStack

from cfg import EDGE_DIRECT, EDGE_CURVES, SCENE_WIDTH, SCENE_HEIGHT


class KMBNodeScene(Serializable):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent  # main editor widget
        self.args_menu = self.parent.args_menu.panel

        self.scene_width = SCENE_WIDTH
        self.scene_height = SCENE_HEIGHT
        self.graphic_scene = KMBNodeGraphicScene(self)
        self.graphic_scene.set_graphic_scene(self.scene_width,
                                             self.scene_height)
        self.history = KMBHistoryStack(self.graphic_scene, self.args_menu)

    # -------------------------------
    #              CHECK
    # -------------------------------

    def check_edge(self, edge, edge_type):
        """ Check edge valid.

        :return -1 (Invalid), 0 (Valid but not ignore), 1 (Valid).
        """
        if edge_type == EDGE_DIRECT:
            # add constraints on Direct(IO) edge.
            # Conditions:
            # 1. <Input> node doesn't accept any input.
            if edge.end_item.gr_name == "Input":
                return -1
            # 2. nodes that cannot be token as i/o.
            if (
                not edge.start_item.as_ipt or
                not edge.end_item.as_ipt or
                not edge.start_item.as_opt or
                not edge.end_item.as_opt
            ):
                return -1
            # 3. Referenced type node doesn't involve in any IO(Direct) edge.
            if (
                edge.end_item.gr_name == "PlaceHolder" or
                edge.start_item.gr_name == "PlaceHolder" or
                edge.end_item.gr_type == 'Units' or
                edge.start_item.gr_type == 'Units'
            ):
                return -1
            # 4. <Model> node cannot be others output.
            if edge.start_item.gr_name == "Model":
                return -1
            # 5. check the same edge in previous edges.
            for e in self.history.edges.values():
                if (
                    (
                        e.start_item == edge.start_item and
                        e.end_item == edge.end_item
                    ) or
                    (
                        e.start_item == edge.end_item and
                        e.end_item == edge.start_item
                    )
                ):
                    return -1
            # io node cannot be token as Wrapper layer's arg anymore.
            edge.start_item.as_arg = False
            edge.end_item.as_arg = False

        elif edge_type == EDGE_CURVES:
            # add constraints on Curve(REF) edge.
            # Conditions:
            # 1. Ref's output must be <Layers> node,
            #    input must be the Referenced type.
            #    Except the nodes which can take layer
            #    as its arg. For example,
            #    <Layer> TimeDistributed & Bidirectional.
            if edge.start_item.gr_type == "Layers":
                # Bidirectional node only accept Recurrent type.
                if (
                    edge.end_item.gr_name == 'Bidirectional' and
                    edge.start_item.gr_sort == 'Recurrent' and
                    edge.start_item.as_arg
                ):
                    edge.start_item.as_ipt = False
                    edge.start_item.as_opt = False
                    return 1
                # TimeDistributed takes Keras layer.
                if (
                    edge.end_item.gr_name == 'TimeDistributed' and
                    edge.start_item.as_arg
                ):
                    edge.start_item.as_ipt = False
                    edge.start_item.as_opt = False
                    return 1
            #   common
            if (
                edge.start_item.gr_type == "Layers" or
                edge.end_item.gr_type != "Layers"
            ):
                return -1
            # 2. <Model> has nothing to do with ref edge.
            if (
                edge.start_item.gr_name == "Model" or
                edge.end_item.gr_name == "Model"
            ):
                return -1
            # 3. check through all the edges,
            # ref curve allow to repeat, but it's very unnecessary to
            # display the edge again, so just display the line once.
            for e in self.history.edges.values():
                if (
                    e.start_item == edge.start_item and
                    e.end_item is edge.end_item
                ):
                    return 0
            # which means ref curves allow user to drag from same node,
            # but it must link to the different arg item.
            # good thing is referenced arg item will be disable,
            # so it's unnecessary to add few more `if` block.
        return 1

    # -------------------------------
    #          MAIN OPERATION
    # -------------------------------

    def add_edge(self, edge):
        self.history.create_edge(edge)

    def remove_edge(self, edge):
        self.history.remove_edge(edge)

    def add_node(self, node):
        self.history.create_node(node)

    def remove_node(self, node):
        self.history.remove_node(node)

    def add_note(self, note):
        self.history.create_note(note)

    def remove_note(self, note):
        self.history.remove_note(note)

    def clear(self):
        self.history.clear()

    # -------------------------------
    #              UTILS
    # -------------------------------

    def get_node_count(self, node_name):
        return self.history.counter.get(node_name)

    def assign_edge_io_type(self, edge_id, io_type):
        # assign i/o type of one edge.
        io_edge = self.history.edges.get(edge_id)
        io_edge.io_type = io_type

    def assign_edge_ref_box(self, edge_id, dst_idx: str):
        # assign ref_box of one edge.
        ref_edge = self.history.edges.get(edge_id)
        ref_edge.ref_box = int(dst_idx)

    # -------------------------------
    #               IO
    # -------------------------------

    def serialize(self):
        # serialize node and edge here.
        nodes = {}
        for node in self.history.nodes.values():
            ns = node.serialize()
            nodes[ns["id"]] = ns
        # serialize note here.
        for note in self.history.notes.values():
            ts = note.serialize()
            nodes[ts["id"]] = ts
        # organize edge's relationship here.
        # fill with node's <input> and <output> tags,
        # and it's only for <layer> node.
        for edge in self.history.edges.values():
            edge_type, edge_from, edge_to = edge.serialize()
            if edge_type != EDGE_DIRECT:
                continue
            # execute only for direct edge.
            from_tag = nodes[edge_from]['tag']
            to_tag = nodes[edge_to]['tag']
            if from_tag == 'layer':
                if to_tag == 'layer':
                    nodes[edge_from]['output'].append(edge_to)
                    nodes[edge_to]['input'].append(edge_from)
                elif to_tag == 'model':
                    nodes[edge_from]['output'].append(edge_to)
        return nodes

    def deserialize(self, feeds: dict, args_menu: KMBArgsMenu):
        # map old node id to new id. (wrapper, graphic)
        node_map = {}

        # First Loop
        for old_id, node in feeds.items():
            if node['recover'] == 'node':
                # deserialize Node
                new_node = KMBNodeItem(self.graphic_scene,
                                       node_name=node['cls'],
                                       node_type=node['type'],
                                       node_sort=node['sort'],
                                       pin_id=None,
                                       parent=self.parent)
                new_node.deserialize(node['x'], node['y'])
                self.history.dump_node(new_node)
                node_map[old_id] = (new_node.id, new_node.gr_node.id_str)
                # deserialize Args: for args models
                if node.__contains__('arg'):
                    args_menu.deserialize(feed=node,
                                          new_nodes=self.history.nodes,
                                          node_map=node_map,
                                          old_id=old_id,
                                          include_args=False)
            elif node['recover'] == 'note':
                # deserialize Note
                new_note = KMBNote(self.graphic_scene,
                                   x=node['x'],
                                   y=node['y'],
                                   with_focus=False)
                new_note.deserialize(node['text'])
                self.history.dump_note(new_note)

        # Second Loop
        for old_id, node in feeds.items():
            # deserialize io Edge by node_map except the one to Model.
            ipts: str = node.get('input')
            opts: str = node.get('output')
            if ipts is not None and opts is not None:
                if opts != 'null':
                    for opt in opts.split(';'):
                        end_id = node_map[opt][0]
                        end_item = self.history.nodes[end_id]
                        # create this edge later.
                        if end_item.gr_name == 'Model':
                            pass
                        else:
                            new_io_edge = KMBEdge(self,
                                                  start_item=self.history.nodes[node_map[old_id][0]],
                                                  end_item=end_item, edge_type=EDGE_DIRECT)
                            self.history.dump_edge(new_io_edge)
                else:
                    # ipts != null and opts == null, is repeating.
                    # ipts == null and opts == null, is nothing.
                    pass
            # deserialize Args: for args
            if node.__contains__('arg'):
                edges = args_menu.deserialize(
                    feed=node,
                    new_nodes=self.history.nodes,
                    node_map=node_map,
                    old_id=old_id,
                    include_args=True
                )  # refs and ios
                if edges is not None:
                    # deserialize ref Edge.
                    for src, (dst, idx) in edges[0].items():
                        new_ref_edge = KMBEdge(self,
                                               start_item=self.history.nodes[src],
                                               end_item=self.history.nodes[dst],
                                               edge_type=EDGE_CURVES)
                        new_ref_edge.ref_box = idx
                        self.history.dump_edge(new_ref_edge)
                    # deserialize Model's io Edge.
                    for src, (dst, io_type) in edges[1].items():
                        new_io_edge = KMBEdge(self,
                                              start_item=self.history.nodes[src],
                                              end_item=self.history.nodes[dst],
                                              edge_type=EDGE_DIRECT)
                        new_io_edge.io_type = io_type
                        self.history.dump_edge(new_io_edge)
