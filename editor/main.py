from PyQt5.QtWidgets import (QMainWindow, QLabel, QAction,
                             QFileDialog, QMessageBox)
from PyQt5.QtGui import QIcon

from editor.widgets.node_editor import MainNodeEditor
from lib.parser import Saver
from cfg import icon, tips


class KMBMainWindow(QMainWindow):

    def __init__(self, screen_size):
        super().__init__()
        self.save_path: str = None

        # init widget
        self.node_editor = MainNodeEditor(self)
        self.status_mouse_pos = QLabel("(x,y)")
        self.toolbar = self.addToolBar('Toolbar')

        # register actions in toolbar
        # ------
        self.action_new = QAction(QIcon(icon['NEW']), '', self)
        self.action_open = QAction(QIcon(icon['OPEN']), '', self)
        self.action_import = QAction(QIcon(icon['IMPORT']), '', self)
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
        self.init_ui(screen_size)

    # --------------------------------------
    #             INITIALIZE
    # --------------------------------------

    def init_ui(self, screen_size):
        width, height = screen_size
        self.setCentralWidget(self.node_editor.splitter)
        self.setWindowTitle('Karken: KMB')
        self.setWindowIcon(QIcon(icon['WINICON']))
        self.setMinimumHeight(height)
        self.setMinimumWidth(width)

    def create_status_bar(self):
        self.statusBar().showMessage("Welcome to Karken: KMB!")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)

    def set_toolbar_tooltip(self):
        # set action tooltips
        self.action_new.setToolTip("Create (Ctrl+N)")
        self.action_open.setToolTip("Open (Ctrl+O)")
        self.action_save.setToolTip("Save (Ctrl+S)")
        self.action_import.setToolTip("Import (Ctrl+I)")
        self.action_export.setToolTip("Export (Ctrl+E)")

        self.action_new.setStatusTip(tips['ST_NEW'])
        self.action_open.setStatusTip(tips['ST_OPEN'])
        self.action_save.setStatusTip(tips['ST_SAVE'])
        self.action_import.setStatusTip(tips['ST_IMPORT'])
        self.action_export.setStatusTip(tips['ST_EXPORT'])
        # ------
        self.action_select.setToolTip("Select (V)")
        self.action_hand.setToolTip("Move (M)")
        self.action_undo.setToolTip("Undo (Ctrl+Z)")
        self.action_redo.setToolTip("Redo (Alt+Z)")

        self.action_select.setStatusTip(tips['ST_SELECT'])
        self.action_hand.setStatusTip(tips['ST_MOVE'])
        self.action_undo.setStatusTip(tips['ST_UNDO'])
        self.action_redo.setStatusTip(tips['ST_REDO'])
        # ------
        self.action_edge_direct.setToolTip("Connect: I/O Direct (D)")
        self.action_edge_curve.setToolTip("Connect: Ref Curve (C)")
        self.action_note.setToolTip("Note (T)")
        self.action_delete.setToolTip("Delete")

        self.action_edge_direct.setStatusTip(tips['ST_EDGE_DIRECT'])
        self.action_edge_curve.setStatusTip(tips['ST_EDGE_CURVES'])
        self.action_note.setStatusTip(tips['ST_NOTE'])
        self.action_delete.setStatusTip(tips['ST_DEL'])
        # ------
        self.action_about.setToolTip("About")

        self.action_about.setStatusTip(tips['ST_ABOUT'])

    def set_toolbar_actions(self):
        # file operation
        self.toolbar.addAction(self.action_new)
        self.action_new.setShortcut('Ctrl+N')
        self.toolbar.addAction(self.action_open)
        self.action_open.setShortcut('Ctrl+O')
        self.toolbar.addAction(self.action_save)
        self.action_save.setShortcut('Ctrl+S')
        self.toolbar.addAction(self.action_import)
        self.action_import.setShortcut('Ctrl+I')
        self.toolbar.addAction(self.action_export)
        self.action_export.setShortcut('Ctrl+E')
        self.toolbar.addSeparator()
        # tool operation
        self.toolbar.addAction(self.action_undo)
        self.action_undo.setShortcut('Ctrl+Z')
        self.toolbar.addAction(self.action_redo)
        self.action_redo.setShortcut('Alt+Z')
        self.toolbar.addAction(self.action_select)
        self.toolbar.addAction(self.action_hand)
        self.toolbar.addSeparator()
        # edge operation
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
        self.action_new.triggered.connect(self.new_)
        self.action_open.triggered.connect(self.open_)
        self.action_save.triggered.connect(self.save_)
        self.action_import.triggered.connect(self.import_)
        self.action_export.triggered.connect(self.export_)
        # ------
        # self.action_undo
        # self.action_redo
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
        # self.action_note
        self.action_delete.triggered.connect(
            self.node_editor.nodes_view.set_delete_mode
        )
        # self.action_about

    # --------------------------------------
    #              OPERATIONS
    # --------------------------------------

    def update_xy_pos(self, x: int, y: int):
        pos = 'POS (x={:>5}, y={:>5})'.format(x, y)
        self.status_mouse_pos.setText(pos)

    def update_modify_state(self):
        # call by node_editor.
        if self.save_path and not self.save_path.endswith('*'):
            self.setWindowTitle(self.save_path + '*')

    # --------------------------------------
    #                ACTIONS
    # --------------------------------------

    def new_(self):
        # create a new module project.
        state = self.node_editor.nodes_view.items()
        if state:
            # current project exists.
            msg_box = QMessageBox()
            msg_box.setText("What are you going to do with current project?")
            msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Save)
        else:
            # current project is the newest.
            msg_box = self._alert_msg_box("Current project is the newest.")
        state = msg_box.exec()
        # actions on different buttons
        if state == QMessageBox.Save:
            # call save method.
            self.save()
        elif state == QMessageBox.Discard:
            # don't save, then clean up.
            self.node_editor.nodes_view.gr_scene.clear()
        # else: ...

    def open_(self):
        # load a module to current project.
        pass

    def save_(self):
        # saving for the first time.
        # check current state
        state = self.node_editor.nodes_view.items()
        if not state:
            msg = self._alert_msg_box("Current project has nothing to save.")
            msg.exec()
            return
        if self.save_path is None:
            file_dialog = QFileDialog()
            file = file_dialog.getSaveFileName(self,
                                               "Saving Module",
                                               "/", "KMB Module (*.kmbm)")
            if file[0]:  # confirm
                self.save_path = file[0]
            else:  # cancel
                return
        # continue saving.
        serialized = self.node_editor.serialize()
        save = Saver(serialized)
        save.save_file(dst=self.save_path)
        # change windows title to current project path.
        self.setWindowTitle(self.save_path.replace('*', ''))

    def import_(self):
        # import some thing to kmb.
        pass

    def export_(self):
        # export current project to a certain file.
        # TODO: a config form then export
        #       return the error from parser if happened.
        pass

    # --------------------------------------
    #                  UTILS
    # --------------------------------------

    @classmethod
    def _alert_msg_box(cls, text: str):
        msg = QMessageBox()
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        return msg
