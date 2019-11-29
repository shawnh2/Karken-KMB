
class Serializable:

    def __init__(self):
        self.id = str(id(self))

    def serialize(self):
        raise NotImplemented

    def deserialize(self, *args, **kwargs):
        raise NotImplemented
