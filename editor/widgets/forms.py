from PyQt5.QtWidgets import (QFormLayout, QDialog, QHBoxLayout, QMessageBox, QFileDialog,
                             QLineEdit, QPushButton, QComboBox, QLabel, QTextEdit)
from PyQt5.QtCore import Qt

from cfg import EXPORT_SUPPORT
from editor.component.pthreads import PyParsingThread


class ExportFormDialog(QDialog):
    """ Form widget for export function. """

    def __init__(self,
                 src_loc: str,
                 parent=None,
                 model_name: str = None,
                 last_author: str = None,
                 last_comment: str = None,
                 last_location: str = None):
        super().__init__(parent)
        self.layout = QFormLayout(self)
        self.commit_layout = QHBoxLayout()

        self.title = QLabel('<h2>Export settings</h2>')
        # all the input form items.
        self.name = QLineEdit(model_name)
        self.author = QLineEdit(last_author)
        self.comments = QTextEdit(last_comment)
        self.format = QComboBox()
        self.location = QPushButton('Choose a location'
                                    if not last_location
                                    else '...' + last_location[-20: -1])
        # two commit buttons.
        self.cancel = QPushButton('Cancel')
        self.confirm = QPushButton('Confirm')

        # recording inputs
        self.src_loc = src_loc
        self.dst_loc: str = last_location
        self.model_name: str = model_name
        self.model_author: str = last_author
        self.model_comment: str = last_comment

        self.prepare()
        self.setup_body()
        self.setFixedSize(300, 370)

    def __call__(self, *args, **kwargs):
        self.exec()

    def prepare(self):
        # for layout
        self.layout.setVerticalSpacing(15)
        self.name.setMinimumSize(170, 25)
        self.author.setMinimumSize(170, 25)
        self.comments.setMaximumSize(170, 100)
        self.comments.setPlaceholderText('Optional')
        self.location.setMinimumSize(185, 25)
        self.location.setToolTip(self.dst_loc)
        # for combobox
        self.format.addItems(EXPORT_SUPPORT)
        self.format.setMinimumSize(180, 25)
        # trigger
        self.location.clicked.connect(self.set_location)
        self.cancel.clicked.connect(self.close)
        self.confirm.clicked.connect(self.commit)

    def setup_body(self):
        self.layout.addRow(self.title)
        self.layout.addRow('Model Name', self.name)
        self.layout.addRow('Author', self.author)
        self.layout.addRow('Comments', self.comments)
        self.layout.addRow('Format', self.format)
        self.layout.addRow('Location', self.location)
        # two commit buttons
        self.commit_layout.addWidget(self.cancel, alignment=Qt.AlignLeft)
        self.commit_layout.addWidget(self.confirm, alignment=Qt.AlignRight)
        self.layout.addRow('', self.commit_layout)

    # ----------FUNCTIONS----------

    def set_location(self):
        file = QFileDialog()
        path = file.getExistingDirectory(self, 'Choose a location to export', '/',
                                         QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if path:
            self.dst_loc = path
            self.location.setText('...' + self.dst_loc[-20: -1])
            self.setToolTip(self.dst_loc)

    def commit(self):
        state = self.check_integrity()
        # uncompleted form.
        if not state[0]:
            state[1].exec()
        # completed form.
        else:
            PyParsingThread(self.src_loc,
                            self.dst_loc,
                            self.model_name,
                            self.model_author,
                            self.model_comment,
                            self)()

    # ----------UTILS----------

    def check_integrity(self) -> (bool, QMessageBox):
        msg_box = QMessageBox()
        msg_box.setStandardButtons(QMessageBox.Close)
        msg_box.setDefaultButton(QMessageBox.Close)
        msg = 'Please assign the {} of this module.'
        state = True
        # model name
        if not self.name.text():
            msg_box.setText(msg.format('name'))
            state = False
        else:
            self.model_name = self.name.text().replace(' ', '_')
        # model author
        if not self.author.text():
            msg_box.setText(msg.format('author'))
            state = False
        else:
            self.model_author = self.author.text()
        # model comment optional
        if self.comments.toPlainText():
            self.model_comment = self.comments.toPlainText()
        # export location
        if not self.dst_loc:
            msg_box.setText(msg.format('location'))
            state = False

        return state, msg_box

    def get_inputs(self):
        # get current form's inputs.
        return self.model_author, self.model_comment, self.dst_loc


class ImportFormDialog(QDialog):
    pass
