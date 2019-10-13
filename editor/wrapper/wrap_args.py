from editor.widgets.node_args import KMBNodesArgsMenu
from editor.wrapper.serializable import Serializable


class KMBArgsMenu(Serializable):

    def __init__(self, parent=None):
        super().__init__()
        self.panel = KMBNodesArgsMenu(self, parent)

    def serialize(self):
        # k is id, v is model(ArgEditableModel)
        for k, v in self.panel.edit_model.items():
            # filter out every items that has been changed
            pass

    def deserialize(self):
        pass
