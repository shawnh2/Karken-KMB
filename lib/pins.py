import os


class CustomPins:
    """ Saving for custom pins. """

    def __init__(self):
        if not os.path.exists('user'):
            os.mkdir('user')
        self.location = 'user/'

    def dump(self, pin):
        pass

    def load(self, pin):
        pass

    def remove(self, pin):
        pass
