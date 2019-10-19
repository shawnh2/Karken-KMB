""" The counter that count the number of node. """


class Counter:

    def __init__(self):
        self._count = {}

    def update(self, obj):
        key = self._serial(obj)
        if self._count.__contains__(key):
            self._count[key] += 1
        else:
            self._count[key] = 0

    def get(self, obj):
        key = self._serial(obj)
        return self._count.get(key)

    @classmethod
    def _serial(cls, obj):
        return str(id(obj))
