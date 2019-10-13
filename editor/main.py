from PyQt5.QtWidgets import QMainWindow, QLabel, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from editor.widgets.node_editor import MainNodeEditor
from cfg import icon


class KMBMainWindow(QMainWindow):

    def __init__(self, screen_size):
        super().__init__()

        # init widget
        self.node_editor = MainNodeEditor(self)
        self.status_mouse_pos = QLabel("(x,y)")
        self.toolbar = self.addToolBar('Toolbar')

        # register actions in toolbar
        self.action_select = QAction(QIcon(icon['ARROW']), '', self)
        self.action_hand = QAction(QIcon(icon['HAND']), '', self)
        self.action_delete = QAction(QIcon(icon['DELETE']), '', self)
        self.action_line_s = QAction(QIcon(icon['SLINE']), '', self)
        self.action_line_c = QAction(QIcon(icon['CLINE']), '', self)
        self.set_toolbar_tooltip()
        self.set_toolbar_actions()
        self.set_toolbar_trigger()

        # init status bar
        self.create_status_bar()

        # init main window
        self.init_slots()
        self.init_ui(screen_size)

    def init_ui(self, screen_size):
        width, height = screen_size
        self.setCentralWidget(self.node_editor)
        self.setWindowTitle('Karken: KMB')
        self.setWindowIcon(QIcon(icon['WINICON']))
        self.setMinimumHeight(height)
        self.setMinimumWidth(width)
        self.show()

    def init_slots(self):
        # update x,y pos label
        self.node_editor.nodes_view.scene_pos_changed.connect(
            self.update_xy_pos
        )

    def create_status_bar(self):
        self.statusBar().showMessage("Welcome to Karken: KMB!")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)

    def set_toolbar_tooltip(self):
        # set action tooltips
        self.action_select.setToolTip("Select")
        self.action_hand.setToolTip("Move")
        self.action_delete.setToolTip("Delete")
        self.action_line_s.setToolTip("Connect (Straight)")
        self.action_line_c.setToolTip("Connect (Curve)")

    def set_toolbar_actions(self):
        # file operation
        self.toolbar.addSeparator()
        # tool operation
        self.toolbar.addAction(self.action_select)
        self.toolbar.addAction(self.action_hand)
        self.toolbar.addSeparator()
        # line operation
        self.toolbar.addAction(self.action_line_s)
        self.toolbar.addAction(self.action_line_c)
        self.toolbar.addAction(self.action_delete)
        self.toolbar.addSeparator()

    def set_toolbar_trigger(self):
        # add triggered function

        self.action_select.triggered.connect(
            self.node_editor.nodes_view.set_select_mode
        )
        self.action_hand.triggered.connect(
            self.node_editor.nodes_view.set_movable_mode
        )
        self.action_delete.triggered.connect(
            self.node_editor.nodes_view.set_delete_mode
        )

        self.action_line_s.triggered.connect(
            self.node_editor.nodes_view.set_line_s_mode
        )
        self.action_line_c.triggered.connect(print)

    def update_xy_pos(self, x: int, y: int):
        pos = f'POS:(x={x: 5}, y={y: 5})'
        self.status_mouse_pos.setText(pos)
