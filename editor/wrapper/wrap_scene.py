from editor.graphic.node_scene import KMBNodeGraphicScene
from editor.wrapper.serializable import Serializable
from cfg import EDGE_DIRECT, EDGE_CURVES, color
from lib import Counter, debug


class KMBNodeScene(Serializable):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent  # main editor widget
        self.edges = {}  # saving wrapper edges
        self.nodes = {}  # saving wrapper nodes
        self.nodes_counter = Counter()  # count the nodes

        self.scene_width = 10000
        self.scene_height = 10000
        self.graphic_scene = KMBNodeGraphicScene(self)
        self.graphic_scene.set_graphic_scene(self.scene_width,
                                             self.scene_height)

    def check_node(self):
        """ Don't need now. """
        pass

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
            # 2. Referenced type node doesn't involve in any IO(Direct) edge.
            if (
                    edge.end_item.gr_name == "PlaceHolder" or
                    edge.start_item.gr_name == "PlaceHolder" or
                    edge.end_item.gr_type == 'Units' or
                    edge.start_item.gr_type == 'Units'
            ):
                return -1
            # 3. <Model> node cannot be others output.
            if edge.start_item.gr_name == "Model":
                return -1
            # 4. check the same edge in previous edges.
            for e in self.edges.values():
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

        elif edge_type == EDGE_CURVES:
            # add constraints on Curve(REF) edge.
            # Conditions:
            # 1. Ref's output must be <Layers> node,
            #    input must be the Referenced type.
            #    Except the nodes which can take layer
            #    as its arg. For example,
            #    <Layer> TimeDistributed & Bidirectional.
            if (
                    edge.start_item.gr_type == "Layers" and
                    edge.end_item.gr_name in
                    ("TimeDistributed", "Bidirectional")):
                return 1
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
            for e in self.edges.values():
                if (e.start_item == edge.start_item and
                        e.end_item is edge.end_item):
                    return 0
            # which means ref curves allow user to drag from same node,
            # but it must link to the different arg item.
            # good thing is referenced arg item will be disable,
            # so it's unnecessary to add few more `if` block.
        return 1

    def add_edge(self, edge):
        self.edges[edge.id] = edge
        debug(f"*[EDGE {len(self.edges)}] + {edge}")

    def remove_edge(self, edge):
        try:
            self.edges.pop(edge.id)
            debug(f"*[EDGE {len(self.edges)}] - {edge}")
        except KeyError:
            debug(f"*[EDGE IGNORE] - {edge}")

    def add_node(self, node):
        self.nodes[node.id] = node
        self.nodes_counter.update(node.gr_name)
        debug(f"*[NODE {len(self.nodes)}] + {node}")

    def remove_node(self, node):
        try:
            self.nodes.pop(node.id)
            self._remove_relative_edges(node)
            debug(f"*[NODE {len(self.nodes)}] - {node}")
        except KeyError:
            debug(f"*[NODE IGNORE] - {node}")

    def _remove_relative_edges(self, node):
        # removing node also remove edge that connected to it.
        edges = self.edges.copy()
        # cannot iter self.edges directly that's ...
        for edge in edges.values():
            if node == edge.start_item or node == edge.end_item:
                self.graphic_scene.removeItem(edge.gr_edge)
                self.remove_edge(edge)  # ... because of this.

    def get_node_count(self, node):
        return self.nodes_counter.get(node.gr_name)

    def change_color_for_io(self, edge_id, io_type):
        """ The edge to Model has two different dot color. """
        io_edge = self.edges.get(edge_id)
        if io_type == 'i':
            dot_color = color['DOT_IO_I']
        else:
            dot_color = color['DOT_IO_O']
        io_edge.update_dot_color(dot_color)

    def serialize(self):
        # serialize node and edge here.
        # fill with node's <input> and <output> tags.
        nodes = {}
        for node in self.nodes.values():
            ns = node.serialize()
            nodes[ns["id"]] = ns
        # organize edge's relationship here.
        # only for <layer> node.
        for edge in self.edges.values():
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

    def deserialize(self):
        pass
