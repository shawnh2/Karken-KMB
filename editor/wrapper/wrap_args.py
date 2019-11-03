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
        # get <args> element in <layer>
        args_dict = OrderedDict()
        vars_name_dict = {}
        for id_, model in self.panel.edit_model.items():
            args_dict[id_] = model.extract_args(get_changed=True,
                                                get_referenced=True)
            vars_name_dict[id_] = model.var_name
        return args_dict, vars_name_dict

    def deserialize(self):
        pass
