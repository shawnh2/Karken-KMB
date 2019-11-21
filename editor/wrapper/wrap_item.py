from editor.graphic.node_item import KMBNodeGraphicItem
from editor.wrapper.serializable import Serializable
from lib import tagger


class KMBNodeItem(Serializable):

    def __init__(self, scene,
                 node_name: str,
                 node_type: str,
                 node_sort: str,
                 pin_id,
                 parent):
        super().__init__()
        self.gr_scene = scene
        self.gr_name = node_name
        self.gr_type = node_type  # CATEGORY
        self.gr_sort = node_sort  # SORT
        self.pin_id = pin_id      # also can be marked as a pin.
        self.parent = parent
        self.gr_node = KMBNodeGraphicItem(self,
                                          self.gr_name,
                                          self.gr_sort,
                                          self.parent)
        self.gr_scene.addItem(self.gr_node)

        self.as_arg = True  # whether can be token as some Wrapper layer's arg.
        self.as_io = True   # whether can be other node's i/o.

    def __repr__(self):
        return f"<NodeItem {id(self)}>"

    def set_pos(self, x, y):
        self.gr_node.set_pos(x, y)

    def update_connect_edges(self):
        for edge in self.gr_scene.scene.edges.values():
            edge.update_positions()

    def serialize(self):
        # common tag here:
        node_id = self.gr_node.id_str

        # None value key will assign later.
        if self.gr_name == 'PlaceHolder':
            # tag for PlaceHolder:
            tag = tagger(
                tag='ph',
                id=node_id,
                var=None
            )
        elif self.gr_name == 'Model':
            # tag for Model:
            tag = tagger(
                tag='model',
                id=node_id,
                var=None,
                class_=self.gr_name,
                args=None
            )
        elif self.gr_type == 'Units':
            # tag for Units:
            tag = tagger(
                tag='unit',
                id=node_id,
                var=None,
                class_=self.gr_name,
                args=None,
                # # #
                type=self.gr_sort.lower()
            )
        else:
            # tag for Layers:
            tag = tagger(
                tag='layer',
                id=node_id,
                var=None,
                class_=self.gr_name,
                args=None,
                # # #
                # [mode] can be 'IO', 'CA' or 'AC', which stands for:
                # Input/Output, Callable and Acceptable.
                # The node usually use direct edge to represent IO relation,
                # so in that case, the [mode] will be 'IO'.
                # However, some layers are able to accept others as their args,
                # under this scenario, the one that accept one layer as its arg
                # will be 'AC', those which are accepted by 'AC' will be 'CA' anyway.
                mode='IO' if self.gr_name not in ('TimeDistributed', 'Bidirectional') else 'AC',
                # the 'CA' will be assigned later.
                input=[],
                output=[]
            )
        return tag

    def deserialize(self):
        pass
