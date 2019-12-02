from editor.graphic.node_scene import KMBNodeGraphicScene
from editor.graphic.node_note import KMBNote
from editor.wrapper.wrap_edge import KMBEdge
from editor.wrapper.wrap_item import KMBNodeItem
from editor.wrapper.serializable import Serializable

from cfg import EDGE_DIRECT, EDGE_CURVES, color
from lib import Counter, debug


class KMBNodeScene(Serializable):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent  # main editor widget
        self.edges = {}  # saving wrapper edges
        self.nodes = {}  # saving wrapper nodes
        self.notes = {}  # saving the notes
        self.nodes_counter = Counter()  # count the nodes

        self.scene_width = 10000
        self.scene_height = 10000
        self.graphic_scene = KMBNodeGraphicScene(self)
        self.graphic_scene.set_graphic_scene(self.scene_width,
                                             self.scene_height)

    # -------------------------------
    #              CHECK
    # -------------------------------

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
            # 2. nodes that cannot be token as i/o.
            if not edge.start_item.as_io or not edge.end_item.as_io:
                return -1
            # 3. Referenced type node doesn't involve in any IO(Direct) edge.
            if (
                edge.end_item.gr_name == "PlaceHolder" or
                edge.start_item.gr_name == "PlaceHolder" or
                edge.end_item.gr_type == 'Units' or
                edge.start_item.gr_type == 'Units'
            ):
                return -1
            # 4. <Model> node cannot be others output.
            if edge.start_item.gr_name == "Model":
                return -1
            # 5. check the same edge in previous edges.
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
            # io node cannot be token as Wrapper layer's arg anymore.
            edge.start_item.as_arg = False
            edge.end_item.as_arg = False

        elif edge_type == EDGE_CURVES:
            # add constraints on Curve(REF) edge.
            # Conditions:
            # 1. Ref's output must be <Layers> node,
            #    input must be the Referenced type.
            #    Except the nodes which can take layer
            #    as its arg. For example,
            #    <Layer> TimeDistributed & Bidirectional.
            if edge.start_item.gr_type == "Layers":
                # Bidirectional node only accept Recurrent type.
                if (
                    edge.end_item.gr_name == 'Bidirectional' and
                    edge.start_item.gr_sort == 'Recurrent' and
                    edge.start_item.as_arg
                ):
                    edge.start_item.as_io = False
                    return 1
                # TimeDistributed takes Keras layer.
                if (
                    edge.end_item.gr_name == 'TimeDistributed' and
                    edge.start_item.as_arg
                ):
                    edge.start_item.as_io = False
                    return 1
            #   common
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
                if (
                    e.start_item == edge.start_item and
                    e.end_item is edge.end_item
                ):
                    return 0
            # which means ref curves allow user to drag from same node,
            # but it must link to the different arg item.
            # good thing is referenced arg item will be disable,
            # so it's unnecessary to add few more `if` block.
        return 1

    # -------------------------------
    #          MAIN OPERATION
    # -------------------------------

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

    def add_note(self, note):
        self.notes[note.id] = note
        debug(f"*[NOTE {len(self.notes)}] + {note}")

    def remove_note(self, note):
        self.notes.pop(note.id)
        debug(f"*[NOTE {len(self.notes)}] - {note}")

    def clear(self):
        # clear all the items that stored.
        self.nodes.clear()
        self.edges.clear()
        self.notes.clear()
        self.nodes_counter.clear()

    # -------------------------------
    #              UTILS
    # -------------------------------

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

    # -------------------------------
    #               IO
    # -------------------------------

    def serialize(self):
        # serialize node and edge here.
        nodes = {}
        for node in self.nodes.values():
            ns = node.serialize()
            nodes[ns["id"]] = ns
        # serialize note here.
        for note in self.notes.values():
            ts = note.serialize()
            nodes[ts["id"]] = ts
        # organize edge's relationship here.
        # fill with node's <input> and <output> tags,
        # and it's only for <layer> node.
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

    def deserialize(self, feeds: dict, args_menu):
        # todo: create io edge, relation here.
        io_map = {}  # map old node id to new id.
        for old_id, node in feeds.items():
            if node['recover'] == 'node':
                # deserialize Node
                new_node = KMBNodeItem(self.graphic_scene,
                                       node_name=node['cls'],
                                       node_type=node['type'],
                                       node_sort=node['sort'],
                                       pin_id=None,
                                       parent=self.parent)
                new_node.deserialize(node['x'], node['y'])
                self.add_node(new_node)
                io_map[old_id] = new_node.id
                # deserialize Args
                if node.get('arg') is not None:
                    args_menu.deserialize(new_node, node['arg'])
            elif node['recover'] == 'note':
                # deserialize Note
                new_note = KMBNote(self.graphic_scene,
                                   x=node['x'],
                                   y=node['y'],
                                   with_focus=False)
                new_note.deserialize(node['text'])
                self.add_note(new_note)
        # deserialize io Edge by io_map.
        for old_id, node in feeds.items():
            ipt = node.get('input')
            opt = node.get('output')
            if ipt is not None and opt is not None:
                if opt != 'null':
                    new_edge = KMBEdge(self,
                                       start_item=self.nodes[io_map[old_id]],
                                       end_item=self.nodes[io_map[opt]],
                                       edge_type=EDGE_DIRECT)
                    self.add_edge(new_edge)
                else:
                    # ipt != null and opt == null, is repeating.
                    # ipt == null and opt == null, is nothing.
                    pass
