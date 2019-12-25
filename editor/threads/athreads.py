""" Some animation threads """
from PyQt5.QtCore import QThread, QPointF

from cfg import SCENE_WIDTH, SCENE_HEIGHT


class OrganizeThread(QThread):
    """ A thread for organizing the nodes pos.
    Basically, split one scene into matrix, and
    change the node pos to the nearest cell center. """

    def __init__(self, node_set: dict, parent=None):
        """
        initialize

        :param node_set: a dict full of nodes wrapper.
        :param parent: its parent.
        """
        super().__init__(parent)
        self.node_set = node_set
        self.cell_size = 100.0
        self.map_center_x = SCENE_WIDTH // 2
        self.map_center_y = SCENE_HEIGHT // 2

    def __call__(self):
        self.run()

    def run(self):
        records = set()  # avoid repeating
        for node in self.node_set.values():
            gr_node = node.gr_node
            old_x, old_y = self.map_to_global(gr_node.pos())
            row, col = self.cell_nearest_pos(old_x, old_y)
            # check repeating
            if (row, col) in records:
                row += 1
            else:
                records.add((row, col))
            new_x, new_y = self.map_to_scene(row, col)
            gr_node.move_to_pos(new_x, new_y)

    def cell_nearest_pos(self, x: float, y: float):
        # calculate the node belong to which cell.
        i = int(x / self.cell_size)
        j = int(y / self.cell_size)
        # find the pos of nearest cell.
        cell_x = i * self.cell_size + self.cell_size // 2
        cell_y = j * self.cell_size + self.cell_size // 2
        return cell_x, cell_y

    def map_to_global(self, pos: QPointF):
        # map scene pos to global pos.
        gx = self.map_center_x + pos.x()
        gy = self.map_center_y - pos.y()
        return gx, gy

    def map_to_scene(self, x: float, y: float):
        # map global pos to scene pos.
        sx = x - self.map_center_x
        sy = self.map_center_y - y
        return sx, sy
