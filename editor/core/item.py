from editor.widgets.node_item import KMBNodeGraphicItem


class KMBNodeItem():

    def __init__(self, scene, node_name):
        self.scene = scene
        self.node = KMBNodeGraphicItem(self, node_name)

        self.scene.addItem(self.node)

    def set_pos(self, x, y):
        self.node.set_pos(x, y)
