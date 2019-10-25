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
        return color['DTC_numseq'], 'Num/Seq'
    elif datatype == 'mut':
        return color['DTC_mut'], 'Mutable'
    else:
        return color['DTC_unknown'], 'Unknown'


def reorder_args_box(head, heap: list) -> list:
    """
    Set the heap list first value to become head value.

    :param head: the first value want to become.
    :param heap: where store all the value.
    :return: a head value first heap (list).
    """

    assert head in heap
    head_idx = heap.index(head)
    heap[0], heap[head_idx] = heap[head_idx], heap[0]
    return heap


def debug(*msg):
    """
    If it's under debug mode, then print the msg.

    :param msg: debug message
    :return: null
    """
    if DEBUG:
        print(*msg)
