""" All kinds of Errors that may happen during parsing. """


# ------ PyParser Type Error------

class PyParsingError(Exception):
    """
    All the errors that happen during parsing to [.py],
    should inherit this Exception.
    """
    def __init__(self, *args):
        self.args = args


class PyMissingInputError(PyParsingError):
    """
    Occur when the parser doesn't get any entrance.
    Which means the model doesn't own any Input node.
    """
    def __str__(self):
        return "Failure:\nThis model doesn't have any Input node."


class PyMissingModelError(PyParsingError):
    """
    This model doesn't have endpoint.
    Which means the model doesn't own any Model node.
    """
    def __str__(self):
        return "Failure:\nThis model doesn't have any Model node."


class PyMissingRequiredArgumentError(PyParsingError):
    """ Missing the required argument. """
    def __str__(self):
        return "Failure:\nMissing required argument at\n{}".format(*self.args)


class PyMissingNecessaryConnectionError(PyParsingError):
    """ Missing necessary connection edge. """
    def __str__(self):
        return "Failure:\nMissing necessary connection at\n{}".format(*self.args)


# ------ PyParser Type Warning------

class PyParsingWarning(Exception):
    """
    All the warnings that happen during parsing to [.py],
    should inherit this Exception.
    """
    def __init__(self, *args):
        self.args = args


class PyExistedFileWarning(PyParsingWarning):
    """ Having existed same name file in current directory. """
    def __str__(self):
        return "Warning:\nExisted file in current directory."


class PyUnusedNodeWarning(PyParsingWarning):
    """ Having existed but never used node in file. """
    def __str__(self):
        return "Warning:\n{} node was never used.".format(*self.args)
