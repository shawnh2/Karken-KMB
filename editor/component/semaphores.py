from collections import OrderedDict

from PyQt5.QtGui import QColor

from cfg import color
from lib import debug


class ReferenceToSemaphore:
    """ It's maintained in ArgEditItem. """
    pass


class ReferenceBySemaphore:
    """ The semaphore of referenced. """

    def __init__(self):
        self._ref_by_dict = {}
        self._ref_by_vn_dict = {}
        self.update_flag = False
        self.ref_color = QColor(color['ARG_REFED'])

    def add(self, ref_by: tuple):
        node_id, ref_item, node_vn_item = ref_by
        # the structure of _ref_by_dict:
        # { node(id): {item(id): item(instance), ...}, ... }
        self._ref_by_dict.setdefault(node_id, {})[str(id(ref_item))] = ref_item
        # store the var name item of dst node.
        # { node(id): var_name_item(instance), ... }
        if not self._ref_by_vn_dict.__contains__(node_id):
            self._ref_by_vn_dict[node_id] = node_vn_item

    def get(self):
        return self._ref_by_dict

    def get_var_name(self, node_id: str):
        dst_vn_item = self._ref_by_vn_dict.get(node_id)
        return dst_vn_item.text() if dst_vn_item else 'Error'

    def destroy(self):
        """ ! This method deletes ALL ref relations in _ref_by_dict. """
        # no necessary to change ref_by_update_flag to False.
        # because once this func has been called,
        # its entire instance will be destroyed.
        for ref_dict in self._ref_by_dict.values():
            for ref in ref_dict.values():
                debug(f'[DEL REF] {ref} ref has been removed.')
                del ref.ref_to
        # clean all
        self._ref_by_dict = {}
        self._ref_by_vn_dict = {}

    def update(self, value: str):
        if self.update_flag:
            # update every item that has a ref relation with self.
            for ref_dict in self._ref_by_dict.values():
                for ref in ref_dict.values():
                    if ref.tag == 0:
                        ref.setBackground(self.ref_color)
                    if value.startswith('@'):
                        pass  # avoid trapping in recursion.
                    elif value == '':
                        pass  # value got deleted.
                    else:
                        ref.value = '@' + value
                    debug(f'[UPDATE] {ref} => {value}')
            # set back the flag.
            self.update_flag = False

    def popup(self, node_id: str, ref_id: str):
        """ ! This method only deletes ONE ref relation in _ref_by_dict. """
        # remove one ref_by in ref_by_dict.
        ref_dict = self._ref_by_dict.get(node_id)
        # only if there's one item in that dict,
        # the ref_id can be set to None.
        # if ref_id is None, then del its whole dict.
        if ref_id is None:
            ref_id, ref_item = ref_dict.popitem()
        # else remove that ref item in dict.
        else:
            ref_item = ref_dict.get(ref_id)
            ref_dict.pop(ref_id)
        del ref_item.ref_to
        debug(f'[DEL REF] at node: {node_id} arg: {ref_id}')
        # check dict empty.
        if len(ref_dict) == 0:
            self._ref_by_dict.pop(node_id)
            self._ref_by_vn_dict.pop(node_id)

    def count(self, node_id: str):
        return len(self._ref_by_dict.get(node_id))


class ModelIOSemaphore:
    """ The semaphore of model's inputs and outputs. """

    def __init__(self, owner):
        self._owner = owner
        self._inputs = OrderedDict()
        self._outputs = OrderedDict()

    def add(self, io: tuple):
        node_id, sign, node_vn_item = io
        assert sign in ('i', 'o'), f'got {sign} instead'
        if sign == 'i':
            self._inputs[node_id] = node_vn_item
        else:
            self._outputs[node_id] = node_vn_item
        debug(f'[IO {sign}pt] add {node_id} in {self._owner.var_name}')

    def get(self):
        return self._inputs, self._outputs

    def popup(self, node_id):
        # pop up while deleting io edge.
        if node_id in self._inputs:
            self._inputs.pop(node_id)
            debug(f'[DEL I] at {node_id}')
        elif node_id in self._outputs:
            self._outputs.pop(node_id)
            debug(f'[DEL O] at {node_id}')

    def order(self, order_key: list, io_type: str):
        # change the order of io
        assert io_type in ('i', 'o')
        new_dict = OrderedDict.fromkeys(order_key)
        if io_type == 'i':
            for key in new_dict.keys():
                new_dict[key] = self._inputs[key]
            self._inputs = new_dict
        else:
            for key in new_dict.keys():
                new_dict[key] = self._outputs[key]
            self._outputs = new_dict
