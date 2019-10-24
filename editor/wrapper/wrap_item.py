from editor.graphic.node_item import KMBNodeGraphicItem
from editor.wrapper.serializable import Serializable


class KMBNodeItem(Serializable):

    def __init__(self, scene, node_name, node_type):
        super().__init__()
        self.gr_scene = scene
        self.gr_name = node_name
        self.gr_type = node_type
        self.gr_node = KMBNodeGraphicItem(self, self.gr_name)

        self.gr_scene.addItem(self.gr_node)

    def __repr__(self):
        return f"<NodeItem {hex(id(self))}>"

    def set_pos(self, x, y):
        self.gr_node.set_pos(x, y)

    def update_connect_edges(self):
        for edge in self.gr_scene.scene.edges:
            if edge.is_available():
                edge.update_positions()

    def serialize(self):
        return {
            "tag": "layer",
            "id": str(id(self.gr_node)),
            "class": self.gr_name,
            "mode": 'IO',
            "input": [],
            "output": [],
            "var": None,  # None: assign it later
            "args": None
        }

    def deserialize(self):
        pass
