from PyQt5.QtWidgets import QMainWindow, QLabel, QAction, QToolBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from editor.widgets import MainNodeEditor


class KMBMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # init UI
        self.node_editor = MainNodeEditor(self)
        self.setCentralWidget(self.node_editor)

        # setting up status bar
        self.status_mouse_pos = QLabel("(x,y)")
        self.create_status_bar()

        # setting up toolbar
        # register an action
        self.action_select_mode = QAction(QIcon('editor/icon/arrow.png'), '', self)
        self.action_hand_mode = QAction(QIcon('editor/icon/hand.png'), '', self)
        # set action tooltips
        self.action_select_mode.setToolTip("Select")
        self.action_hand_mode.setToolTip("Move")
        # add it to the toolbar
        self.toolbar = self.addToolBar('Toolbar')
        # file operation
        self.toolbar.addSeparator()
        # tool operation
        self.toolbar.addAction(self.action_select_mode)
        self.toolbar.addAction(self.action_hand_mode)
        self.toolbar.addSeparator()
        # add triggered function
        self.action_select_mode.triggered.connect(
            self.node_editor.nodes_view.set_select_mode
        )
        self.action_hand_mode.triggered.connect(
            self.node_editor.nodes_view.set_movable_mode
        )

        # update x,y pos label
        self.node_editor.nodes_view.scene_pos_changed.connect(
            self.update_xy_pos
        )

        self.setWindowTitle('Karken: KMB')
        self.setGeometry(400, 200, 1330, 750)
        self.show()

    def create_status_bar(self):
        self.statusBar().showMessage("Welcome to Karken: KMB!")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)

    def update_xy_pos(self, x: int, y: int):
        pos = f'({x},{y})'
        self.status_mouse_pos.setText(pos)
