from editor.widgets.node_item import KMBNodeGraphicItem
from editor.core.serializable import Serializable


class KMBNodeItem(Serializable):

    def __init__(self, scene, node_name):
        super().__init__()
        self.gr_scene = scene
        self.gr_name = node_name
        self.gr_node = KMBNodeGraphicItem(self, self.gr_name)

        self.gr_scene.addItem(self.gr_node)

    def set_pos(self, x, y):
        self.gr_node.set_pos(x, y)

    def serialize(self):
        pass

    def deserialize(self):
        pass
