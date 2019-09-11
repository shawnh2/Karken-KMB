from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.QtCore import Qt

from editor.widgets import MainNodeEditor


class KMBMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # init UI
        self.node_editor = MainNodeEditor(self)
        self.setCentralWidget(self.node_editor)

        self.status_mouse_pos = QLabel("pos")

        self.create_status_bar()

        self.setWindowTitle('Karken: KMB')
        self.setGeometry(400, 200, 1330, 750)
        self.show()

    def create_status_bar(self):
        self.statusBar().showMessage("this is a status bar!")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
