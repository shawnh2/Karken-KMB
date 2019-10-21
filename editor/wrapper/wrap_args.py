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
        # TODO: rebuild there
        # <args> element that lives in <layer>
        args_dict = OrderedDict()
        vars_name_dict = {}
        for id_, model in self.panel.edit_model.items():
            arg_dict = OrderedDict()
            var_name = ""
            # filter every items that has been changed
            idx = 0
            check_idx = 0  # idx for check-box
            combo_idx = 0  # idx for combo-box
            while True:
                arg_name = model.item(idx, 0)
                # stop when arg goes end
                if arg_name is None:
                    break
                # tell different arg type by its tag
                arg_value = model.item(idx, 1)
                if arg_value.tag == 0:  # normal-input
                    if arg_name.text() == 'var_name':
                        var_name = arg_value.text()
                    elif arg_value.is_changed:
                        arg_dict[arg_name.text()] = arg_value.text()

                elif arg_value.tag == 1:  # check-box
                    if model.check_args[check_idx][3]:
                        arg_dict[arg_name.text()] = model.check_args[check_idx][2]
                    check_idx += 1

                elif arg_value.tag == 2:  # combo-box
                    if model.combo_args[combo_idx][5]:
                        arg_dict[arg_name.text()] = model.combo_args[combo_idx][4]
                    combo_idx += 1
                idx += 1
            args_dict[id_] = arg_dict
            vars_name_dict[id_] = var_name
        return args_dict, vars_name_dict

    def deserialize(self):
        pass
