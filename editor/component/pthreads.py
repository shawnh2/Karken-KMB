""" Wrap parser into QThread. """

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMessageBox

from cfg import icon
from lib.parser import Saver, Loader
from lib.parser import PyParser, PyHandler, PyParsingError


class SavingThread(QThread):

    def __init__(self, serialized, dst: str):
        super().__init__()
        self.saver = Saver(serialized, dst)

    def __call__(self, *args, **kwargs):
        self.run()

    def run(self):
        self.saver.save_file()


class LoadingThread(QThread):

    def __init__(self, src: str, editor):
        super().__init__()
        self.loader = Loader(src)
        self.editor = editor

    def __call__(self, *args, **kwargs):
        self.run()

    def run(self):
        loads = self.loader.load_file()
        self.editor.deserialize(loads)


class PyParsingThread(QThread):

    def __init__(self, src, dst, name, author, comment, parent):
        super().__init__()
        self.src = src
        self.dst = dst
        self.name = name
        self.author = author
        self.comment = comment
        self.parent = parent
        self.error = QPixmap(icon['EXPORT_ERR'])

    def __call__(self, *args, **kwargs):
        self.run()

    def run(self):
        try:
            parser = PyParser(self.src)
            handler = PyHandler(parser, self.name, self.author, self.comment)
            handler.export(self.dst)
        except PyParsingError as err:
            msg = QMessageBox()
            msg.setText(str(err))
            msg.setIconPixmap(self.error)
            msg.setWindowTitle('Export Error')
            msg.setWindowIcon(QIcon(icon['WINICON']))
            msg.setStandardButtons(QMessageBox.Close)
            msg.exec()
        finally:
            self.parent.close()
