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
        # ------
        self.action_new = QAction(QIcon(icon['NEW']), '', self)
        self.action_open = QAction(QIcon(icon['OPEN']), '', self)
        self.action_save = QAction(QIcon(icon['SAVE']), '', self)
        self.action_export = QAction(QIcon(icon['EXPORT']), '', self)
        # ------
        self.action_select = QAction(QIcon(icon['ARROW']), '', self)
        self.action_hand = QAction(QIcon(icon['HAND']), '', self)
        self.action_undo = QAction(QIcon(icon['UNDO']), '', self)
        self.action_redo = QAction(QIcon(icon['REDO']), '', self)
        # ------
        self.action_delete = QAction(QIcon(icon['DELETE']), '', self)
        self.action_edge_direct = QAction(QIcon(icon['SLINE']), '', self)
        self.action_edge_curve = QAction(QIcon(icon['CLINE']), '', self)
        self.action_note = QAction(QIcon(icon['NOTE']), '', self)
        # ------
        self.action_about = QAction(QIcon(icon['ABOUT']), '', self)
        self.set_toolbar_tooltip()
        self.set_toolbar_actions()
        self.set_toolbar_trigger()
        self.set_toolbar_style()

        # init status bar
        self.create_status_bar()

        # init main window
        self.init_slots()
        self.init_ui(screen_size)

    # --------------------------------------
    #             INITIALIZE
    # --------------------------------------

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
        self.action_new.setToolTip("Create(Ctrl+N)")
        self.action_new.setEnabled(False)
        self.action_open.setToolTip("Open(Ctrl+O)")
        self.action_open.setEnabled(False)
        self.action_save.setToolTip("Save(Ctrl+S)")
        self.action_export.setToolTip("Export(Ctrl+E)")
        self.action_export.setEnabled(False)
        self.action_select.setToolTip("Select(V)")
        self.action_hand.setToolTip("Move(M)")
        self.action_undo.setToolTip("Undo(Ctrl+Z)")
        self.action_undo.setEnabled(False)
        self.action_redo.setToolTip("Redo(Alt+Z)")
        self.action_redo.setEnabled(False)
        self.action_delete.setToolTip("Delete")
        self.action_edge_direct.setToolTip("Connect I/O Direct(D)")
        self.action_edge_curve.setToolTip("Connect Curve(C)")
        self.action_edge_curve.setEnabled(False)
        self.action_note.setToolTip("Note(T)")
        self.action_note.setEnabled(False)
        self.action_about.setToolTip("About")
        self.action_about.setEnabled(False)

    def set_toolbar_actions(self):
        # file operation
        self.toolbar.addAction(self.action_new)
        self.toolbar.addAction(self.action_open)
        self.toolbar.addAction(self.action_save)
        self.toolbar.addAction(self.action_export)
        self.toolbar.addSeparator()
        # tool operation
        self.toolbar.addAction(self.action_undo)
        self.toolbar.addAction(self.action_redo)
        self.toolbar.addAction(self.action_select)
        self.toolbar.addAction(self.action_hand)
        self.toolbar.addSeparator()
        # line operation
        self.toolbar.addAction(self.action_edge_direct)
        self.toolbar.addAction(self.action_edge_curve)
        self.toolbar.addAction(self.action_note)
        self.toolbar.addAction(self.action_delete)
        self.toolbar.addSeparator()
        # others
        self.toolbar.addAction(self.action_about)

    def set_toolbar_style(self):
        for action in self.toolbar.actions():
            widget = self.toolbar.widgetForAction(action)
            widget.setFixedSize(38, 35)

    def set_toolbar_trigger(self):
        # add triggered function
        # ------
        self.action_save.triggered.connect(self.save)
        # ------
        self.action_select.triggered.connect(
            self.node_editor.nodes_view.set_select_mode
        )
        self.action_hand.triggered.connect(
            self.node_editor.nodes_view.set_movable_mode
        )
        # ------
        self.action_edge_direct.triggered.connect(
            self.node_editor.nodes_view.set_edge_direct_mode
        )
        self.action_edge_curve.triggered.connect(
            self.node_editor.nodes_view.set_edge_curve_mode
        )
        self.action_delete.triggered.connect(
            self.node_editor.nodes_view.set_delete_mode
        )
        # ------

    # --------------------------------------
    #              OPERATIONS
    # --------------------------------------

    def update_xy_pos(self, x: int, y: int):
        pos = f'POS:(x={x: 5}, y={y: 5})'
        self.status_mouse_pos.setText(pos)

    def save(self):
        self.node_editor.serialize()
