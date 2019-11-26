""" Wrap parser into QThread. """
from PyQt5.QtCore import QThread

from editor.component.messages import PopMessageBox
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
        self.ok_msg = PopMessageBox('Export Success', run=True)
        self.error_msg = PopMessageBox('Export Error', run=True)
        self.warns_msg = PopMessageBox('Export Warning', run=True)

    def __call__(self, *args, **kwargs):
        self.run()

    def run(self):
        try:
            parser = PyParser(self.src)
            handler = PyHandler(parser, self.name, self.author, self.comment)
            warnings, count = handler.export(self.dst)
            if count > 0:
                self.warns_msg.make('Export complete but got {} warnings.'.format(count),
                                    PopMessageBox.TYPE_EXPORT_WARNING, extra_text=warnings)
            else:
                self.ok_msg.make('Export complete.', PopMessageBox.TYPE_OK)
        except PyParsingError as err:
            self.error_msg.make(str(err), PopMessageBox.TYPE_EXPORT_ERROR)
        finally:
            self.parent.close()
