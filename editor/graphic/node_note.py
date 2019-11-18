from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from cfg import color
from lib import debug


class KMBNote(QGraphicsTextItem):

    def __init__(self, scene, x, y, parent=None):
        super().__init__(parent)
        self.pr_scene = scene
        self.pr_scene.addItem(self)

        # TODO: null text is refused;
        #       make 4 arrow key work;
        #       solve conflict with hot-key;
        #       set background color;
        self.setFlags(QGraphicsTextItem.ItemIsSelectable | QGraphicsTextItem.ItemIsMovable)
        self.setTextInteractionFlags(Qt.TextEditable)
        self.setDefaultTextColor(Qt.white)
        self.setAcceptHoverEvents(True)
        self.setPos(x + 5, y - 12)
        self.setTextWidth(100)
        self.setFocus()

    def hoverEnterEvent(self, event):
        self.setDefaultTextColor(QColor(color['NOTE_HOVER']))

    def hoverLeaveEvent(self, event):
        self.setDefaultTextColor(Qt.white)

    def focusOutEvent(self, event):
        if self.toPlainText() == '':
            debug('[REMOVE EMPTY NOTE]')
        else:
            self.setTextInteractionFlags(Qt.NoTextInteraction)

    def mouseDoubleClickEvent(self, event):
        # double click to edit text.
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus()
