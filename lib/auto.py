import re
import string


class AutoInspector:
    """
    Inspect the input value of arg item,
    inspect and correct it.
    Test: see test/test_ai.py.

    Support type: String, Number, Sequence.
    You can add your own inspector by writing a method
    here with prefix `_inspect_ ` + `TYPE NAME`.
    """

    def __init__(self):
        self._cur_value = None

    def auto_type_check(self, value: str, dtype: str):
        self._cur_value = value
        # facing different cases.
        try:
            new_value = eval(f'self._inspect_{dtype.lower()}()')
            return new_value
        except AttributeError:
            # if got no support type, then return without any check.
            return value

    def _inspect_string(self):
        """ Fill the empty char with '_'. """
        name = self._cur_value.strip().lower()
        if name[0].isdigit():
            name = '_' + name
        # get rid of all the invalid char
        for p in string.punctuation:
            # expect underline: '_'
            if p == '_':
                continue
            name = name.replace(p, '')
        return name.replace(' ', '_')

    def _inspect_number(self):
        """ Number check.
        Will extract number like `-XX.XX`.
        But if you have one non-digit char like
        `-XXc.XX`, it will be like `-XXXX`.
        This kind of char has interrupt function.
        `-XX.cXX`, this form works well(`-XX.XX`).
        """
        nbr = re.compile('-?\d+\.?\d*')
        res = nbr.findall(self._cur_value)
        if len(res) == 0:
            return str(len(self._cur_value))
        return ''.join(res)

    def _inspect_sequence(self):
        """ Fill with brackets.
        KMB also will inspect the seq type by the
        first bracket. For example, if you type:
        => [1, 2, 3   >>>   [1, 2, 3]
        => (1, 2, 3   >>>   (1, 2, 3)
        or
        => 1, 2, 3]   >>> (1, 2, 3)
        => 1, 2, 3)   >>> (1, 2, 3)
        or even
        => 1, 2, 3    >>> (1, 2, 3)  !! Tuple is default type.
        or worse
        => [1, 2, 3)  >>> [1, 2, 3]  !! Follow the first bracket.
        The separator default is `,` if without it:
        => 12.34      >>> (12.34,)
        or use separator
        => 12;3       >>> (12, 12, 12)
        => [12;3      >>> [12, 12, 12]
        => 12;2;3     >>> (12, 12)   !! Only first two is valid.
        => 12;        >>> (12, 12)   !! Default times is 2.
        and also only digit is valid.
        """
        def semicolon_split(value: str):
            # Basic form N;t
            # only works on first two split value.
            split = value.split(';')
            nbr, times = split[0], split[1]
            # has `;` but not t
            if times == '':
                return [nbr, nbr]
            return [nbr for _ in range(int(times))]

        # setup bracket type
        if self._cur_value.startswith('[') or \
           self._cur_value.startswith(']'):
            l_br = '['
            r_br = ']'
        else:
            l_br = '('
            r_br = ')'
        # replace bracket all and reassign.
        for b in ('(', ')', '[', ']'):
            self._cur_value = self._cur_value.replace(b, '')
        pattern = re.compile('-?\d+\.?\d*;?\d*')
        separated = []
        for res in pattern.findall(self._cur_value):
            if res.__contains__(';'):
                res = semicolon_split(res)
                separated += res
            else:
                separated.append(res)
        # finally return the result.
        # if cannot find any number, so input may be invalid,
        # and under this situation, return a array that full of zero.
        if len(separated) == 0:
            separated = ['0' for _ in range(len(self._cur_value))]
        # only one item will be lonely,
        # add a comma, like '(X)' -> '(X, )'
        if len(separated) == 1:
            separated = [separated[0] + ', ']
        return l_br + ", ".join([ch for ch in separated]) + r_br
