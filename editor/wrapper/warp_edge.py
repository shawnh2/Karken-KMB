from editor.component.edge_type import KMBGraphicEdgeDirect, KMBGraphicEdgeBezier
from editor.wrapper.serializable import Serializable
from cfg import EDGE_CURVES, EDGE_DIRECT


class KMBEdge(Serializable):

    def __init__(self, scene, start_item, end_item, edge_type):
        super().__init__()
        self.scene = scene  # the wrapper of gr-scene
        # start/end item also is the wrapper of gr-node
        self.start_item = start_item
        self.end_item = end_item
        self.edge_type = edge_type

        if self.edge_type == EDGE_DIRECT:
            self.gr_edge = KMBGraphicEdgeDirect(self)
        elif self.edge_type == EDGE_CURVES:
            self.gr_edge = KMBGraphicEdgeBezier(self)
        # add edge on graphic scene
        self.scene.graphic_scene.addItem(self.gr_edge)

        if self.start_item is not None:
            self.update_positions()

    def __str__(self):
        return f"<Edge {hex(id(self))}>"

    def __repr__(self):
        return f"<Edge {hex(id(self))}>"

    def store(self):
        """ Check state of storing into scene's edges. """
        check_state = self.scene.check_edge(self, self.edge_type)
        if check_state != -1:
            if check_state == 1:
                self.scene.add_edge(self)
            if self.edge_type == EDGE_CURVES:
                self.end_item.gr_node.feed_ref(self.start_item)
            return check_state
        return -1

    def update_positions(self):
        patch = self.start_item.gr_node.width / 2
        src_pos = self.start_item.gr_node.pos()
        self.gr_edge.set_src(src_pos.x()+patch, src_pos.y()+patch)
        if self.end_item is not None:
            end_pos = self.end_item.gr_node.pos()
            self.gr_edge.set_dst(end_pos.x()+patch, end_pos.y()+patch)
        else:
            self.gr_edge.set_dst(src_pos.x()+patch, src_pos.y()+patch)
        self.gr_edge.update()

    def remove_from_current_items(self):
        self.end_item = None
        self.start_item = None

    def remove(self):
        self.remove_from_current_items()
        self.scene.graphic_scene.removeItem(self.gr_edge)
        self.gr_edge = None

    def serialize(self):
        return (str(id(self.start_item.gr_node)),
                str(id(self.end_item.gr_node)))

    def deserialize(self):
        pass
