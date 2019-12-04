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

    def deserialize(self, feed: dict, new_nodes: dict, node_map: dict, old_id: str, include_args=False):
        """ Call this method twice. First finish creating models; handle args at last. """
        # retrieve args from deserialize dict.
        node_id = node_map[old_id][0]
        gr_node_id = node_map[old_id][1]
        node = new_nodes[node_id]

        # First Call
        if not include_args:
            # store a brand new model.
            self.panel.commit_node(
                node_name=node.gr_name,
                node_type=node.gr_type,
                node_id=gr_node_id,
                count=0)
            # set var name
            model = self.panel.fetch_node(gr_node_id)
            model.set_var_name(feed['var'])
            return

        # Second Call
        else:
            ref_edges = {}  # node wrapper id. from: to.
            # modify the value of items.
            model = self.panel.fetch_node(gr_node_id)
            # if it's null, then early stop.
            if not feed['arg']:
                return

            for name, filed in feed['arg'].items():
                value, dtype = filed
                # required but got nothing.
                if value == '!REQ':
                    continue

                query = model.get_item_by_name(name)
                if query is None:
                    # got unfamiliar type of arg here.
                    raise LoadingError(name, node.gr_name,
                                       code=LoadingError.GOT_UNFAMILIAR_ARG)
                else:
                    # reassign the value by different dtype.
                    idx, item = query
                    if dtype == 'id':
                        try:
                            dst_id = node_map[value]
                            dst_node = self.panel.fetch_node(dst_id[1])
                        except KeyError:
                            raise LoadingError(node.gr_name,
                                               code=LoadingError.GOT_MEMORY_ERROR)
                        else:
                            if name in ('inputs', 'outputs'):  # io
                                model.io = (dst_id[1], name[0], dst_node.var_name_item)
                            else:  # ref
                                item.ref_to = (dst_id[1], dst_node.var_name_item)
                                dst_node.ref_by = (gr_node_id, item, model.var_name_item)
                                ref_edges[dst_id[0]] = node_id
                    else:
                        if item.tag == 0:
                            model.reassign_value(item, value)
                        elif item.tag == 1:
                            model.reassign_state(idx, value)
                        elif item.tag == 2:
                            model.reassign_item(idx, value)
                        else:
                            raise LoadingError(item.tag, code=LoadingError.GOT_UNKNOWN_TAG)
            return ref_edges
