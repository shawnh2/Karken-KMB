from editor.graphic.node_item import KMBNodeGraphicItem
from editor.wrapper.serializable import Serializable
from lib import tagger


class KMBNodeItem(Serializable):

    def __init__(self, scene,
                 node_name: str,
                 node_type: str,
                 node_sort: str):
        super().__init__()
        self.gr_scene = scene
        self.gr_name = node_name
        self.gr_type = node_type  # CATEGORY
        self.gr_sort = node_sort  # SORT
        self.gr_node = KMBNodeGraphicItem(self,
                                          self.gr_name,
                                          self.gr_sort)
        self.gr_scene.addItem(self.gr_node)

    def __repr__(self):
        return f"<NodeItem {hex(id(self))}>"

    def set_pos(self, x, y):
        self.gr_node.set_pos(x, y)

    def update_connect_edges(self):
        for edge in self.gr_scene.scene.edges:
            edge.update_positions()

    def serialize(self):
        return tagger(
            tag='layer',
            id=str(id(self.gr_node)),
            class_=self.gr_name,
            mode='IO',
            input=[],
            output=[],
            var=None,  # None: assign it later
            args=None
        )

    def deserialize(self):
        pass
