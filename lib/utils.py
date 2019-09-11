
def split_args_id(id_string: str) -> list:
    """
    Split a string that includes id.

    :param id_string: has form: 'nbr', 'nbr;nbr;nbr', 'nbr-nbr'.
    :return: an id list.
    """

    res = []
    id_string = id_string.split(';')
    for s in id_string:
        if '-' in s:
            start, end = s.split('-')
            res += list(range(int(start), int(end) + 1))
        else:
            res.append(int(s))
    return res


def type_color_map(datatype: str):
    """
    In arguments menu, using color to represent datatype.

    :param datatype: datatype name
    :return: a color hex value and raw datatype name.
    """

    if datatype == 'str':
        return '#00BFFF', 'String'
    elif ('unit-i' in datatype or
          'unit-a' in datatype or
          'unit-c' in datatype or
          'unit-r' in datatype or
          datatype == 'layer' or
          datatype == 'ph'):
        return '#54FF9F', 'Reference'
    elif datatype == 'num':
        return '#FF7256', 'Number'
    elif datatype == 'seq':
        return '#FFB6C1', 'Sequence'
    elif datatype == 'bool':
        return '#CDC9C9', 'Boolean'
    elif datatype == 'num;seq':
        return '#FF83FA', 'Num/Seq'
    else:
        return '#000000', 'Unknown'
