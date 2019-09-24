from editor.widgets.node_item import KMBNodeGraphicItem


class KMBNodeItem():

    def __init__(self, scene, node_name):
        self.gr_scene = scene
        self.gr_name = node_name
        self.gr_node = KMBNodeGraphicItem(self, self.gr_name)

        self.gr_scene.addItem(self.gr_node)

    def set_pos(self, x, y):
        self.gr_node.set_pos(x, y)
