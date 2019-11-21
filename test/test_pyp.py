import os
# set to parent directory
os.chdir(os.path.join(os.getcwd(), ".."))

from lib.parser import PyParser, PyHandler


if __name__ == '__main__':
    parse = PyParser("test/test.kmbm")
    ctt = PyHandler(parse, model_name='Test', author='Shawn')
    ctt.export('test')
