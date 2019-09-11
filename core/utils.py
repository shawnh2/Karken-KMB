

def get_id(obj):
    """
    Get an id number that is unique by using BIF id().

    :param obj: The object that needs an id.
    :return: string with hex form.
    """
    return hex(id(obj))
