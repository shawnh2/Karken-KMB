""" The counter for counting the node number in scene. """

class Counter:

    def __init__(self):
        self._count = {}

    def update(self, obj: str):
        if self._count.__contains__(obj):
            self._count[obj] += 1
        else:
            # start counting from 1
            self._count[obj] = 1

    def get(self, obj: str):
        return self._count.get(obj)
