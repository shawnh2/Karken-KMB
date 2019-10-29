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
            arg_dict = OrderedDict()
            # filter every items that has been ...
            for idx, arg_name, arg_value in model.items():
                if arg_name.text() == 'var_name':
                    vars_name_dict[id_] = arg_value.value
                # ... changed
                elif arg_value.is_changed:
                    arg_dict[arg_name.text()] = arg_value.value
                # ... referenced
                elif arg_value.is_referenced:
                    arg_dict[arg_name.text()] = arg_value.ref_to
            args_dict[id_] = arg_dict
        return args_dict, vars_name_dict

    def deserialize(self):
        pass
