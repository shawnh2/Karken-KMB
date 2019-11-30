from PyQt5.QtWidgets import QMainWindow, QLabel, QAction, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon

from editor.widgets.about import AboutKMB
from editor.widgets.forms import ExportFormDialog
from editor.widgets.node_editor import MainNodeEditor
from editor.component.messages import PopMessageBox
from editor.component.pthreads import SavingThread, LoadingThread
from cfg import icon, tips


class KMBMainWindow(QMainWindow):

    def __init__(self, screen_size):
        super().__init__()
        self.save_path: str = None
        self.last_author: str = None
        self.last_comment: str = None
        self.last_location: str = None
        self.is_modified = False

        # init widget
        self.node_editor = MainNodeEditor(self)
        self.status_mouse_pos = QLabel("(x,y)")
        self.toolbar = self.addToolBar('Toolbar')
        # init attrs
        self.win_title = 'Karken: KMB'
        self.win_icon = QIcon(icon['WINICON'])
        # init common msg box
        self.pop_msg = PopMessageBox(self.win_title, self, run=True)
        self.save_msg = PopMessageBox(self.win_title, self)
        self.save_msg.make("What are you going to do with current project?",
                           PopMessageBox.TYPE_SAVE_OR_NOT)
        self.close_msg = PopMessageBox(self.win_title, self)
        self.close_msg.make("Project has been modified, do you want to save it?",
                            PopMessageBox.TYPE_YES_OR_NO)

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
        self.action_search = QAction(QIcon(icon['SEARCH']), '', self)
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
        self.setWindowTitle(self.win_title)
        self.setWindowIcon(self.win_icon)
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
        self.action_select.setToolTip("Select")
        self.action_hand.setToolTip("Move")
        self.action_undo.setToolTip("Undo (Ctrl+Z)")
        self.action_redo.setToolTip("Redo (Alt+Z)")

        self.action_select.setStatusTip(tips['ST_SELECT'])
        self.action_hand.setStatusTip(tips['ST_MOVE'])
        self.action_undo.setStatusTip(tips['ST_UNDO'])
        self.action_redo.setStatusTip(tips['ST_REDO'])
        # ------
        self.action_edge_direct.setToolTip("Connect: I/O Direct")
        self.action_edge_curve.setToolTip("Connect: Ref Curve")
        self.action_note.setToolTip("Note")
        self.action_delete.setToolTip("Delete")

        self.action_edge_direct.setStatusTip(tips['ST_EDGE_DIRECT'])
        self.action_edge_curve.setStatusTip(tips['ST_EDGE_CURVES'])
        self.action_note.setStatusTip(tips['ST_NOTE'])
        self.action_delete.setStatusTip(tips['ST_DEL'])
        # ------
        self.action_search.setToolTip("Search (Ctrl+F)")
        self.action_search.setStatusTip(tips['ST_SEARCH'])
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
        # common operation
        self.toolbar.addAction(self.action_undo)
        self.action_undo.setShortcut('Ctrl+Z')
        self.toolbar.addAction(self.action_redo)
        self.action_redo.setShortcut('Alt+Z')
        self.toolbar.addAction(self.action_search)
        self.action_search.setShortcut('Ctrl+F')
        self.toolbar.addSeparator()
        # tool operation
        self.toolbar.addAction(self.action_select)
        self.toolbar.addAction(self.action_hand)
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
            widget.setFixedSize(38, 38)

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
        # self.action_search
        # ------
        self.action_select.triggered.connect(
            self.node_editor.nodes_view.set_select_mode
        )
        self.action_hand.triggered.connect(
            self.node_editor.nodes_view.set_movable_mode
        )
        self.action_edge_direct.triggered.connect(
            self.node_editor.nodes_view.set_edge_direct_mode
        )
        self.action_edge_curve.triggered.connect(
            self.node_editor.nodes_view.set_edge_curve_mode
        )
        self.action_note.triggered.connect(
            self.node_editor.nodes_view.set_note_mode
        )
        self.action_delete.triggered.connect(
            self.node_editor.nodes_view.set_delete_mode
        )
        # ------
        self.action_about.triggered.connect(self.about_)

    # --------------------------------------
    #              OPERATIONS
    # --------------------------------------

    def update_xy_pos(self, x: int, y: int):
        pos = 'POS (x={:>5}, y={:>5})'.format(x, y)
        self.status_mouse_pos.setText(pos)

    def update_modify_state(self):
        # call by node_editor.
        self.is_modified = True
        if self.save_path and not self.save_path.endswith('*'):
            self.setWindowTitle(self.save_path + '*')

    # --------------------------------------
    #                ACTIONS
    # --------------------------------------

    def new_(self):
        # create a new module project.
        if not self._cur_proj_is_empty():
            # current project exists.
            state = self.save_msg.exec()
            # actions on different buttons
            if state == QMessageBox.Save:
                # call save method.
                if self.save_():
                    self._drop_cur_proj()
                else:
                    return
            elif state == QMessageBox.Discard:
                self._drop_cur_proj()
            else:
                return
        else:
            # current project is the newest.
            self.pop_msg.make("Current project is the newest.")

    def open_(self):
        # load a module to current project.
        if not self._cur_proj_is_empty():
            # current project exists.
            state = self.save_msg.exec()
            if state == QMessageBox.Save:
                if self.save_():
                    self._open_cur_proj()
                else:
                    return
            elif state == QMessageBox.Discard:
                self._open_cur_proj()
        else:
            # open directly.
            self._open_cur_proj()

    def save_(self, otherwise: str = None) -> bool:
        # saving for the first time.
        # check current state
        if self._cur_proj_is_empty():
            if otherwise:
                self.pop_msg.make("Current project has nothing to {}.".format(otherwise))
            else:
                self.pop_msg.make("Current project has nothing to save.")
            # if merge these two lines, the word in {} may be 'False' sometimes on Windows.
            return False
        if self.save_path is None:
            file_dialog = QFileDialog()
            file = file_dialog.getSaveFileName(self,
                                               "Saving Module",
                                               "/", "KMB Module (*.kmbm)")
            if file[0]:  # confirm
                self.save_path = file[0]
            else:  # cancel
                return False
        # continue saving.
        SavingThread(self.node_editor.serialize(), self.save_path)()
        # change windows title to current project path.
        self.setWindowTitle(self.save_path.replace('*', ''))
        self.is_modified = False
        return True

    def import_(self):
        # import some thing to kmb.
        pass

    def export_(self):
        # export current project to a certain file.
        if self.save_(otherwise='export'):
            model_name = self._get_model_name()
            export = ExportFormDialog(self.save_path,
                                      self, model_name,
                                      self.last_author,
                                      self.last_comment,
                                      self.last_location)
            export.exec()
            (self.last_author,
             self.last_comment,
             self.last_location) = export.get_inputs()
        else:
            self.pop_msg.make('Export has been canceled.')

    def about_(self):
        AboutKMB(self)()

    def closeEvent(self, event):
        if self.is_modified:
            state = self.close_msg.exec()
            if state == QMessageBox.Yes:
                if self.save_():
                    event.accept()
                else:
                    event.ignore()
            elif state == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    # --------------------------------------
    #                  UTILS
    # --------------------------------------

    def _get_model_name(self):
        return self.save_path.split('/')[-1].split('.')[0].capitalize() \
            if self.save_path else None

    def _drop_cur_proj(self):
        # close and clear everything about current project.
        self.node_editor.nodes_view.gr_scene.clear()
        self.node_editor.nodes_scene.clear()
        self.is_modified = False
        self.save_path = None
        self.setWindowTitle('New Project')

    def _open_cur_proj(self):
        # drop current before open project.
        file_dialog = QFileDialog()
        file = file_dialog.getOpenFileName(self,
                                           "Karken: KMB Module File",
                                           "/", "KMB Module (*.kmbm)")
        if file[0]:
            if self.save_path == file[0]:
                self.pop_msg.make('That project is opening now.')
            else:
                self._drop_cur_proj()
                self.save_path = file[0]  # change save path to current.
                LoadingThread(self.save_path, self.node_editor)()
                self.setWindowTitle(self.save_path)
        else:
            return

    def _cur_proj_is_empty(self) -> bool:
        # check whether current project is empty.
        return False if self.node_editor.nodes_view.items() else True
