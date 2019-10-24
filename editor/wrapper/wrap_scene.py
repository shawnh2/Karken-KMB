from editor.graphic.node_scene import KMBNodeGraphicScene
from editor.wrapper.serializable import Serializable
from cfg import DEBUG, EDGE_DIRECT, EDGE_CURVES
from lib import Counter


class KMBNodeScene(Serializable):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent  # main editor widget
        self.edges = []  # saving wrapper edges
        self.nodes = []  # saving wrapper nodes
        self.nodes_counter = Counter()  # count the nodes

        self.scene_width = 16000
        self.scene_height = 16000
        self.graphic_scene = KMBNodeGraphicScene(self)
        self.graphic_scene.set_graphic_scene(self.scene_width,
                                             self.scene_height)

    def check_edge(self, edge, edge_type):
        """ Check edge valid.
        :return -1 (Invalid), 0 (valid but not display), 1 (valid)
        """
        if edge_type == EDGE_DIRECT:
            # check input edge if it's Input or Model
            if edge.end_item.gr_name == "Input" or\
               edge.end_item.gr_name == "PlaceHolder" or\
               edge.start_item.gr_name == "Model" or\
               edge.start_item.gr_name == "PlaceHolder":
                return -1
            # check the same edge in previous edges
            for e in self.edges:
                if e.start_item == edge.start_item and \
                        e.end_item is edge.end_item:
                    return -1
            # which means ref curves allow user to drag from same node,
            # but it must link to the different arg item.
            # good thing is referenced arg item will be disable,
            # so it's unnecessary to add few more `if` block.
        elif edge_type == EDGE_CURVES:
            # ref curve only begins from 'common' or 'other' tab page
            # and end up with 'layers' tab.
            if edge.start_item.gr_type == "Layers" or\
               edge.end_item.gr_type != "Layers":
                return -1
            # ref curve allow to repeat, but it's very unnecessary to
            # display the edge again, just use the first one.
            # but will still store it in memory.
            for e in self.edges:
                if e.start_item == edge.start_item and \
                        e.end_item is edge.end_item:
                    return 0
        # if there's no invalid edge, then return True
        return 1

    def add_edge(self, edge):
        self.edges.append(edge)
        if DEBUG:
            print("*[E_ADD_%d]" % len(self.edges), self.edges)

    def remove_edge(self, edge):
        self.edges.remove(edge)
        if DEBUG:
            print("*[E_DEL_%d]" % len(self.edges), self.edges)

    def add_node(self, node):
        self.nodes.append(node)
        self.nodes_counter.update(node.gr_name)
        if DEBUG:
            print("*[N_ADD_%d]" % len(self.nodes), self.nodes)

    def remove_node(self, node):
        self.nodes.remove(node)
        self._remove_relative_edges(node)
        if DEBUG:
            print("*[N_DEL_%d]" % len(self.nodes), self.nodes)

    def get_node_count(self, node):
        return self.nodes_counter.get(node.gr_name)

    def _remove_relative_edges(self, node):
        # removing node also remove edge that connected to it.
        edges = self.edges.copy()
        # cannot iter self.edges directly that's ...
        for edge in edges:
            if node == edge.start_item or node == edge.end_item:
                self.graphic_scene.removeItem(edge.gr_edge)
                self.remove_edge(edge)  # ... because of this

    def serialize(self):
        # serialize node and edge here
        # fill with node's <input> and <output> tags
        nodes = {}
        for node in self.nodes:
            n = node.serialize()
            nodes[n["id"]] = n
        # organize edge's relationship here
        for edge in self.edges:
            edge_from, edge_to = edge.serialize()
            nodes[edge_from]['output'].append(edge_to)
            nodes[edge_to]['input'].append(edge_from)
        return nodes

    def deserialize(self):
        pass
