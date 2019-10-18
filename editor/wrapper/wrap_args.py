import lxml.html

from editor.widgets.node_args import KMBNodesArgsMenu
from editor.wrapper.serializable import Serializable

etree = lxml.html.etree


class KMBArgsMenu(Serializable):

    def __init__(self, parent=None):
        super().__init__()
        self.panel = KMBNodesArgsMenu(self, parent)

    def serialize(self):
        # <args> element that lives in <layer>
        for id_, model in self.panel.edit_model.items():
            # filter every items that has been changed
            print(id_, model)
            idx = 0
            while True:
                arg_name = model.item(idx, 0)
                # stop when arg goes end
                if arg_name is None:
                    break
                # tell different arg type by its tag
                arg_value = model.item(idx, 1)
                if arg_value.tag == 0:  # edit
                    if arg_value.is_changed:
                        print(arg_value.text())

                elif arg_value.tag == 1:  # check-box
                    print("check")

                elif arg_value.tag == 2:  # combo-box
                    print("combo")
                idx += 1

    def deserialize(self):
        pass
