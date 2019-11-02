
class Serializable:

    def __init__(self):
        self.id = str(id(self))

    def serialize(self):
        raise NotImplemented

    def deserialize(self):
        raise NotImplemented
