from collections import OrderedDict

from editor.widgets.node_args import KMBNodesArgsMenu
from editor.wrapper.serializable import Serializable
from lib.parser import LoadingError


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
                get_required=True,
                get_datatype=True,
                get_io=True
            )
            var_names_dict[node_id] = model.var_name
        return args_dict, var_names_dict

    def deserialize(self, node, feed_args: dict):
        print(feed_args)
        # retrieve args from deserialize dict.
        id_ = node.gr_node.id_str
        # store a brand new model.
        self.panel.commit_node(
            node_name=node.gr_name,
            node_type=node.gr_type,
            node_id=id_,
            count=0)
        # modify the value of items.
        if not feed_args:
            return
        model = self.panel.fetch_node(id_)
        for name, filed in feed_args.items():
            value, dtype = filed
            query = model.get_item_by_name(name)
            if query is None:
                # got unfamiliar type of arg here.
                raise LoadingError(name, node.gr_name,
                                   code=LoadingError.GOT_UNFAMILIAR_ARG)
            else:
                # reassign the value by different dtype.
                idx, item = query
                if dtype == 'id':
                    # todo: ref arg here.
                    pass
                else:
                    if item.tag == 0:
                        model.reassign_value(item, value)
                    elif item.tag == 1:
                        model.reassign_state(idx, value)
                    elif item.tag == 2:
                        model.reassign_item(idx, value)
                    # else: ...
