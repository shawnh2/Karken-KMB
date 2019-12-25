""" All the commands have been hard-coded. """
from PyQt5.QtWidgets import QUndoCommand

from lib import debug
from cfg import EDGE_DIRECT, EDGE_CURVES


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

    def __init__(self, edge, src: dict, args: dict, gr_scene):
        super().__init__()
        self.edge = edge
        self.src = src
        self.args = args
        self.gr_scene = gr_scene

    def after_first_redo(self):
        edge_type = self.edge.gr_edge.type
        dst_gr_node_id = self.edge.end_item.gr_node.id_str
        src_gr_node_id = self.edge.start_item.gr_node.id_str
        dst_model = self.args.get(dst_gr_node_id)
        src_model = self.args.get(src_gr_node_id)

        if edge_type == EDGE_DIRECT:
            if self.edge.end_item.gr_name == 'Model':
                dst_model.io = (src_gr_node_id, self.edge.io_type, src_model.var_name_item)
            else:
                pass
        elif edge_type == EDGE_CURVES:
            dst_item = dst_model.item(self.edge.ref_box, 1)
            dst_item.ref_to = (src_gr_node_id, src_model.var_name_item)
            src_model.ref_by = (dst_gr_node_id, dst_item, dst_model.var_name_item)

        self.gr_scene.addItem(self.edge.gr_edge)
        self.src[self.edge.id] = self.edge
        debug(f"*[EDGE {self.src} ADD] < {self.edge}")

    def undo(self):
        edge_type = self.edge.gr_edge.type
        dst_gr_node_id = self.edge.end_item.gr_node.id_str
        src_gr_node_id = self.edge.start_item.gr_node.id_str
        dst_model = self.args.get(dst_gr_node_id)
        src_model = self.args.get(src_gr_node_id)

        if edge_type == EDGE_DIRECT:
            if self.edge.end_item.gr_name == 'Model':
                dst_model.io_semaphore.popup(src_gr_node_id)
            else:
                pass
        elif edge_type == EDGE_CURVES:
            dst_item = dst_model.item(self.edge.ref_box, 1)
            src_model.rb_semaphore.popup(dst_gr_node_id, dst_item.id_str)

        self.gr_scene.removeItem(self.edge.gr_edge)
        self.src.pop(self.edge.id)
        debug(f"*[EDGE {self.src} ADD] > {self.edge}")


class DeleteEdgeCmd(SkipFirstRedoCommand):

    def __init__(self, edge, src: dict, args: dict, gr_scene):
        super().__init__()
        self.edge = edge
        self.src = src
        self.args = args
        self.gr_scene = gr_scene

    def after_first_redo(self):
        # delete the io & ref relation here.
        edge_type = self.edge.gr_edge.type
        dst_gr_node_id = self.edge.end_item.gr_node.id_str
        src_gr_node_id = self.edge.start_item.gr_node.id_str
        dst_model = self.args.get(dst_gr_node_id)
        src_model = self.args.get(src_gr_node_id)

        if edge_type == EDGE_DIRECT:
            if self.edge.end_item.gr_name == 'Model':
                dst_model.io_semaphore.popup(src_gr_node_id)
            else:
                pass
        elif edge_type == EDGE_CURVES:
            dst_item = dst_model.item(self.edge.ref_box, 1)
            src_model.rb_semaphore.popup(dst_gr_node_id, dst_item.id_str)

        self.gr_scene.removeItem(self.edge.gr_edge)
        self.src.pop(self.edge.id)
        debug(f"*[EDGE {self.src} DEL] < {self.edge}")

    def undo(self):
        # reconnect the io & ref relation here.
        edge_type = self.edge.gr_edge.type
        dst_gr_node_id = self.edge.end_item.gr_node.id_str
        src_gr_node_id = self.edge.start_item.gr_node.id_str
        dst_model = self.args.get(dst_gr_node_id)
        src_model = self.args.get(src_gr_node_id)

        if edge_type == EDGE_DIRECT:
            if self.edge.end_item.gr_name == 'Model':
                dst_model.io = (src_gr_node_id, self.edge.io_type, src_model.var_name_item)
            else:
                pass
        elif edge_type == EDGE_CURVES:
            dst_item = dst_model.item(self.edge.ref_box, 1)
            dst_item.ref_to = (src_gr_node_id, src_model.var_name_item)
            src_model.ref_by = (dst_gr_node_id, dst_item, dst_model.var_name_item)

        self.gr_scene.addItem(self.edge.gr_edge)
        self.src[self.edge.id] = self.edge
        debug(f"*[EDGE {self.src} DEL] > {self.edge}")


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


class NoteUpdateCmd(SkipFirstRedoCommand):

    def __init__(self):
        super().__init__()

    def after_first_redo(self):
        pass

    def undo(self):
        pass


class NodeMoveCmd(SkipFirstRedoCommand):

    def __init__(self):
        super().__init__()

    def after_first_redo(self):
        pass

    def undo(self):
        pass


class ArgItemModifyCmd(SkipFirstRedoCommand):

    def __init__(self):
        super().__init__()

    def after_first_redo(self):
        pass

    def undo(self):
        pass


class GroupDeleteCmd:
    """ Has been tear down to several signal Delete command.
    For example, delete one node will also delete the edge(s) that connected with.
    But undo that, first undo the deleted node, then undo the deleted edge(s). """


class ModelIOOrderChanged:
    pass
