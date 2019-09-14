from editor.widgets import KMBNodesArgsMenu
from editor.widgets.node_args import NodeArgEditItem


class KMBArgsMenu():

    def __init__(self, parent=None):
        self.panel = KMBNodesArgsMenu(self, parent)

        self.changed = []

    def collect_change(self, value: NodeArgEditItem):
        print(value.initial_value, value.text(), value.arg_name)
        self.changed.append(value)
