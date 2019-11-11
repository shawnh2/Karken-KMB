""" Command line version of the parser. """
import os
import argparse

from lib.parser import PyParser, PyHandler


SUPPORT_TYPE = ('.py', )


def parse_args():

    parser = argparse.ArgumentParser(
        description='Parse Karken: KMB model file to a certain type file.')

    parser.add_argument('--src', '-s',
                        help='set the src file path.')
    parser.add_argument('--dst', '-d',
                        default='model.py',
                        help='set the dst file path.')
    parser.add_argument('--type', '-t',
                        default='.py',
                        help='parse the file into certain type.')
    return parser.parse_args()


def check_valid(s, t):

    assert t in SUPPORT_TYPE, \
        f'type should be in {SUPPORT_TYPE}.'

    assert os.path.exists(s), \
        f'{s} does not exist, please check.'


if __name__ == '__main__':
    args = parse_args()

    src = args.src
    dst = args.dst
    typ = args.type
    check_valid(src, typ)

    if typ == '.py':
        py_p = PyParser(src)
        py_h = PyHandler(py_p)
        py_h.export(dst)
