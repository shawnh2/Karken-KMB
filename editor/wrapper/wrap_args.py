from collections import OrderedDict

from editor.widgets.node_args import KMBNodesArgsMenu
from editor.wrapper.serializable import Serializable


class KMBArgsMenu(Serializable):

    def __init__(self, parent=None):
        super().__init__()
        self.panel = KMBNodesArgsMenu(self, parent)

    def fetch(self, key):
        # fetch args model by key: node id
        # result could be model or None
        return self.panel.fetch_node(key)

    def serialize(self):
        # get <args> element for node.
        args_dict = OrderedDict()
        var_names_dict = {}
        for node_id, model in self.panel.edit_model.items():
            args_dict[node_id] = model.extract_args(
                get_changed=True,
                get_referenced=True,
                get_datatype=True,
                get_io=True
            )
            var_names_dict[node_id] = model.var_name
        return args_dict, var_names_dict

    def deserialize(self):
        pass
