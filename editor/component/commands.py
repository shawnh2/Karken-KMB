from PyQt5.QtWidgets import QUndoCommand

from lib import debug


class SkipFirstRedoCommand(QUndoCommand):
    """ Normally undo command will execute redo once it got pushed.
    But this Command will skip the first redo execution. """

    def __init__(self):
        super().__init__()
        self.first = True

    def redo(self):
        # skip the first redo execution.
        if self.first:
            self.first = False
        else:
            self.after_first_redo()

    def after_first_redo(self):
        # redo function will be writen here.
        raise NotImplementedError()


class CreateNodeCmd(SkipFirstRedoCommand):

    def __init__(self, node, src: dict, gr_scene):
        super().__init__()
        self.node = node
        self.src = src
        self.gr_scene = gr_scene

    def after_first_redo(self):
        self.gr_scene.addItem(self.node.gr_node)
        self.src[self.node.id] = self.node
        debug(f"*[NODE {len(self.src)} ADD] < {self.node}")

    def undo(self):
        self.gr_scene.removeItem(self.node.gr_node)
        self.src.pop(self.node.id)
        debug(f"*[NODE {len(self.src)} ADD] > {self.node}")


class DeleteNodeCmd(SkipFirstRedoCommand):

    def __init__(self, node, src: dict, gr_scene):
        super().__init__()
        self.node = node
        self.src = src
        self.gr_scene = gr_scene

    def after_first_redo(self):
        self.gr_scene.removeItem(self.node.gr_node)
        self.src.pop(self.node.id)
        debug(f"*[NODE {len(self.src)} DEL] < {self.node}")

    def undo(self):
        self.gr_scene.addItem(self.node.gr_node)
        self.src[self.node.id] = self.node
        debug(f"*[NODE {len(self.src)} DEL] > {self.node}")


class CreateEdgeCmd(SkipFirstRedoCommand):

    def __init__(self, edge, src: dict, gr_scene):
        super().__init__()
        self.edge = edge
        self.src = src
        self.gr_scene = gr_scene

    def after_first_redo(self):
        self.gr_scene.addItem(self.edge.gr_edge)
        self.src[self.edge.id] = self.edge
        debug(f"*[EDGE {len(self.src)} ADD] < {self.edge}")

    def undo(self):
        self.gr_scene.removeItem(self.edge.gr_edge)
        self.src.pop(self.edge.id)
        debug(f"*[EDGE {len(self.src)} ADD] > {self.edge}")


class DeleteEdgeCmd(SkipFirstRedoCommand):

    def __init__(self, edge, src: dict, gr_scene):
        super().__init__()
        self.edge = edge
        self.src = src
        self.gr_scene = gr_scene

    def after_first_redo(self):
        self.gr_scene.removeItem(self.edge.gr_edge)
        self.src.pop(self.edge.id)
        debug(f"*[EDGE {len(self.src)} DEL] < {self.edge}")

    def undo(self):
        self.gr_scene.addItem(self.edge.gr_edge)
        self.src[self.edge.id] = self.edge
        debug(f"*[EDGE {len(self.src)} DEL] > {self.edge}")


class CreateNoteCmd(SkipFirstRedoCommand):

    def __init__(self, note, src: dict, gr_scene):
        super().__init__()
        self.note = note
        self.src = src
        self.gr_scene = gr_scene

    def after_first_redo(self):
        self.gr_scene.addItem(self.note)
        self.src[self.note.id] = self.note
        debug(f"*[NOTE {len(self.src)} ADD] < {self.note}")

    def undo(self):
        self.gr_scene.removeItem(self.note)
        self.src.pop(self.note.id)
        debug(f"*[NOTE {len(self.src)} ADD] > {self.note}")


class DeleteNoteCmd(SkipFirstRedoCommand):

    def __init__(self, note, src: dict, gr_scene):
        super().__init__()
        self.note = note
        self.src = src
        self.gr_scene = gr_scene

    def after_first_redo(self):
        self.gr_scene.removeItem(self.note)
        self.src.pop(self.note.id)
        debug(f"*[NOTE {len(self.src)} DEL] < {self.note}")

    def undo(self):
        self.gr_scene.addItem(self.note)
        self.src[self.note.id] = self.note
        debug(f"*[NOTE {len(self.src)} DEL] > {self.note}")
