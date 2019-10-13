from editor.component.edge_type import KMBGraphicEdgeDirect
from editor.wrapper.serializable import Serializable


class KMBEdge(Serializable):

    def __init__(self, scene, start_item=None, end_item=None, edge_type=1):
        super().__init__()
        self.scene = scene  # the wrapper of gr-scene

        self._start_item = None
        self._end_item = None

        self.start_item = start_item
        self.end_item = end_item
        self.edge_type = edge_type

    def __str__(self):
        return f"<KMBEdge at {hex(id(self))}>"

    @property
    def start_item(self):
        return self._start_item

    @start_item.setter
    def start_item(self, value):
        if self._start_item is not None:
            self._start_item.remove_edge(self)
        # assign to a new one
        self._start_item = value
        if self.start_item is not None:
            self.start_item.add_edge(self)

    @property
    def end_item(self):
        return self._end_item

    @end_item.setter
    def end_item(self, value):
        if self._end_item is not None:
            self._end_item.remove_edge(self)
        self._end_item = value
        if self.end_item is not None:
            self.end_item.add_edge(self)

    @property
    def edge_type(self):
        return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        self._edge_type = value
        self.gr_edge = KMBGraphicEdgeDirect(self)

        self.scene.graphic_scene.addItem(self.gr_edge)

        if self.start_item is not None:
            self.update_positions()

    def update_positions(self):
        patch = self.start_item.gr_node.width / 2
        src_pos = self.start_item.gr_node.pos()
        self.gr_edge.set_src(src_pos.x()+patch, src_pos.y()+patch)
        if self.end_item is not None:
            end_pos = self.end_item.gr_node.pos()
            self.gr_edge.set_dst(end_pos.x()+patch, end_pos.y()+patch)
        else:
            self.gr_edge.set_src(src_pos.x()+patch, src_pos.y()+patch)
        self.gr_edge.update()

    def remove_from_current_items(self):
        self.end_item = None
        self.start_item = None

    def remove(self):
        self.remove_from_current_items()
        self.scene.graphic_scene.removeItem(self.gr_edge)
        self.gr_edge = None

    def serialize(self):
        pass

    def deserialize(self):
        pass
