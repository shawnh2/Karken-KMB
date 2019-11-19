from cfg import color, DEBUG


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


def type_color_map(datatype: str) -> tuple:
    """
    In arguments menu, using color to represent datatype.

    :param datatype: datatype name
    :return: a color hex value and raw datatype name.
    """

    if datatype == 'str':
        return color['DTC_str'], 'String'
    elif ('unit-i' in datatype or
          'unit-a' in datatype or
          'unit-c' in datatype or
          'unit-r' in datatype or
          datatype == 'layer' or
          datatype == 'ph'):
        return color['DTC_ref'], 'Reference'
    elif datatype == 'num':
        return color['DTC_num'], 'Number'
    elif datatype == 'seq':
        return color['DTC_seq'], 'Sequence'
    elif datatype == 'bool':
        return color['DTC_bool'], 'Boolean'
    elif datatype == 'num;seq':
        return color['DTC_numseq'], 'Num_Seq'
    elif datatype == 'mut':
        return color['DTC_mut'], 'Mutable'
    else:
        return color['DTC_unknown'], 'Unknown'


def type_tag_map(arg_value_item):
    """
     Mapping datatype to tag needs.

     :param arg_value_item.
     :return: A dtype for tag.
     """
    # unwrap from arg value item.
    dtype = arg_value_item.dtype
    dtype_dict = {
        'String': 'str',
        'Reference': 'id',
        'Number': 'num',
        'Sequence': 'seq',
        'Boolean': 'bool',
        'Num_Seq': 'num',
        'Unknown': None
    }
    # Reference and String type may both be 'id'.
    if dtype == 'Reference':
        try:
            arg_value_item.ref_to
        except AttributeError:
            return 'str'
        else:
            return 'id'
    return dtype_dict.get(dtype)


def debug(*msg):
    """
    If it's under debug mode, then print debug msg.

    :param msg: debug message
    :return: null
    """
    if DEBUG:
        print(*msg)


def tagger(**kwargs):
    """
    Make a dict that represent tag.

    :param kwargs: key is tag, value is arg
    :return: a dict
    """
    return dict(**kwargs)


def load_stylesheet(path: str):
    """ Load stylesheet from certain file. """
    with open(path) as f:
        style = f.readlines()
        style = ''.join(style).strip('\n')
    return style
