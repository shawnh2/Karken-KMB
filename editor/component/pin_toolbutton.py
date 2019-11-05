from PyQt5.QtWidgets import QToolButton, QMenu, QAction
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QSize

from lib import remove_custom_pin


class PinToolBox(QToolButton):
    """ Pin Tool button in Node menu. """

    def __init__(self,
                 parent,
                 text: str,
                 tooltip: str,
                 icon_path: str,
                 icon_size: int,
                 signal: str,
                 refresh_button):
        super().__init__(parent)

        self.pin_name = text
        self.pin_id = int(signal.split('-')[4])
        self.refresh = refresh_button

        self.setText(self.pin_name)
        self.setToolTip(tooltip)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(icon_size, icon_size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setObjectName(signal)

        # set right menu for tool button
        self.right_menu = QMenu()
        self.setContextMenuPolicy(Qt.DefaultContextMenu)

    def contextMenuEvent(self, event):
        # make title
        title = QAction(f'{self.pin_name}')
        title.setDisabled(True)
        self.right_menu.addAction(title)
        self.right_menu.addSeparator()
        # make body
        body = self.get_right_menu_body()
        self.right_menu.addActions(body)
        # show
        self.right_menu.exec(QCursor.pos())

    def get_right_menu_body(self):
        """ Operations that will execute on Pin. """
        delete = QAction('Delete it')
        delete.triggered.connect(self.delete_action)

        export = QAction('Export it')
        export.triggered.connect(self.export_action)
        return delete, export

    # ----------ACTIONS----------

    def delete_action(self):
        remove_custom_pin(self.pin_id)
        self.refresh.click()

    def export_action(self):
        pass
