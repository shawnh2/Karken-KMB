from PyQt5.QtWidgets import QUndoStack

from editor.component.commands import CreateNodeCmd, CreateEdgeCmd, CreateNoteCmd
from editor.component.commands import DeleteNodeCmd, DeleteEdgeCmd, DeleteNoteCmd
from lib import Counter, debug


class KMBHistoryStack(QUndoStack):

    def __init__(self, gr_scene, args_menu):
        super().__init__()
        self._nodes = {}
        self._edges = {}
        self._notes = {}

        self.gr_scene = gr_scene
        self.args_menu = args_menu
        self.counter = Counter()
        self.setUndoLimit(30)

    @property
    def nodes(self):
        return self._nodes

    def dump_node(self, node):
        self._nodes[node.id] = node

    def create_node(self, node):
        self.dump_node(node)
        self.counter.update(node.gr_name)
        self.push(CreateNodeCmd(node, self._nodes, self.gr_scene))
        debug(f"*[NODE {len(self._nodes)}] + {node}")

    def remove_node(self, node):
        try:
            self._nodes.pop(node.id)
            self._remove_relative_edges(node)
            self.push(DeleteNodeCmd(node, self._nodes, self.gr_scene))
            debug(f"*[NODE {len(self._nodes)}] - {node}")
        except KeyError:
            debug(f"*[NODE NOT EXIST AND IGNORE] - {node}")

    @property
    def edges(self):
        return self._edges

    def dump_edge(self, edge):
        self._edges[edge.id] = edge

    def create_edge(self, edge):
        self.dump_edge(edge)
        self.push(CreateEdgeCmd(edge, self._edges,
                                self.args_menu.edit_model, self.gr_scene))
        debug(f"*[EDGE {len(self._edges)}] + {edge}")

    def remove_edge(self, edge):
        if edge.id in self._edges:
            self._edges.pop(edge.id)
            del_cmd = DeleteEdgeCmd(edge, self._edges,
                                    self.args_menu.edit_model, self.gr_scene)
            self.push(del_cmd)
            debug(f"*[EDGE {len(self._edges)}] - {edge}")
        else:
            debug(f"*[EDGE NOT EXIST AND IGNORE] - {edge}")

    def destroy_edge(self, edge):
        # destroy one edge without saving into command stack.
        self._edges.pop(edge.id)

    @property
    def notes(self):
        return self._notes

    def dump_note(self, note):
        self._notes[note.id] = note

    def create_note(self, note):
        self.dump_note(note)
        self.push(CreateNoteCmd(note, self._notes, self.gr_scene))
        debug(f"*[NOTE {len(self._notes)}] + {note}")

    def remove_note(self, note):
        self._notes.pop(note.id)
        self.push(DeleteNoteCmd(note, self._notes, self.gr_scene))
        debug(f"*[NOTE {len(self._notes)}] - {note}")

    # -------------UTILS------------

    def clear(self):
        super().clear()  # clear stack
        self._nodes.clear()
        self._edges.clear()
        self._notes.clear()
        self.counter.clear()

    def _remove_relative_edges(self, node):
        # removing node also remove edge that connected to it.
        edges = self._edges.copy()
        for edge in edges.values():
            if node == edge.start_item or node == edge.end_item:
                self.gr_scene.removeItem(edge.gr_edge)
                self.remove_edge(edge)
