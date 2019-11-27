""" Wrap parser into QThread. """
from PyQt5.QtCore import QThread

from editor.component.messages import PopMessageBox
from lib.parser import ExportError
from lib.parser import Saver, Loader
from lib.parser import PyParser, PyHandler


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


class ExportThread(QThread):

    FMT_PY = 0
    FMT_SS_PNG = 1

    def __init__(self, fmt: int, *args, parent):
        super().__init__()
        self.fmt = fmt
        self.args = args
        self.parent = parent
        # msg box
        self.msg_ok = PopMessageBox('Export Success', run=True)
        self.msg_err = PopMessageBox('Export Error', run=True)
        self.msg_warn = PopMessageBox('Export Warning', run=True)

    def __call__(self, *args, **kwargs):
        self.run()

    def run(self):
        try:
            w, c = self._execute()
            # exception handler.
            # success but with warnings.
            if c > 0:
                self.msg_warn.make('Export complete but got {} warnings.'.format(c),
                                   PopMessageBox.TYPE_EXPORT_WARNING, extra_text=w)
            # invalid export.
            elif c < 0:
                self.msg_err.make('Unfamiliar export format!')
            # success. c = 0
            else:
                self.msg_ok.make('Export complete.', PopMessageBox.TYPE_OK)
        except ExportError as err:
            self.msg_err.make(str(err), PopMessageBox.TYPE_EXPORT_ERROR)
        finally:
            self.parent.close()

    def _execute(self):
        """
        All parse function will bring in this method.
        :return: warning_str, count_int.
        """
        if self.fmt == self.FMT_PY:
            res = self._run_fmt_py()
        elif self.fmt == self.FMT_SS_PNG:
            res = self._run_fmt_ss_png()
        # elif: add more here.
        else:
            res = ('', -1)  # invalid fmt.
        return res

    def _run_fmt_py(self):
        src, dst, name, author, comment = self.args
        parser = PyParser(src)
        handler = PyHandler(parser, name, author, comment)
        return handler.export(dst)

    def _run_fmt_ss_png(self):
        _, dst, name, author, _ = self.args
        return '', -1
