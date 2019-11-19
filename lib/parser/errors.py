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
        return "Failure: This model doesn't have any Input node."


class PyMissingModelError(PyParsingError):
    """
    This model doesn't have endpoint.
    Which means the model doesn't own any Model node.
    """
    def __str__(self):
        return "Failure: This model doesn't have any Model node."


class PyMissingRequiredArgument(PyParsingError):
    """ Missing the required argument. """
    def __str__(self):
        return "Failure: Missing required argument - {}".format(self.args)
