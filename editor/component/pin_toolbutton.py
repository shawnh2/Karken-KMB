from PyQt5.QtWidgets import QToolButton, QMenu, QAction
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QSize


class PinToolBox(QToolButton):
    """ Pin Tool button in Node menu. """

    def __init__(self,
                 parent,
                 text: str,
                 tooltip: str,
                 icon_path: str,
                 icon_size: int,
                 signal: str):
        super().__init__(parent)

        self.pin_name = text

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
        title = QAction(f'Selected: {self.pin_name}')
        title.setDisabled(True)
        self.right_menu.addAction(title)
        self.right_menu.addSeparator()
        # make body
        # body = self.get_right_menu_body()
        # self.right_menu.addActions(body)
        # show
        self.right_menu.exec(QCursor.pos())

    def get_right_menu_body(self):
        """ Operations that will execute on Pin. """
        operations = (
            'delete this pin',
            'export this pin',
            'reset this pin',
        )
        actions = []
        for operation in operations:
            action = QAction(operation)
            actions.append(action)
        return actions
