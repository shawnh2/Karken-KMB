from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt, QRectF

from cfg import color
from lib import debug, tagger
from editor.wrapper.serializable import Serializable


class KMBNote(QGraphicsTextItem, Serializable):

    def __init__(self, gr_scene, x, y, parent=None, with_focus=True):
        super().__init__(parent)
        self.gr_scene = gr_scene
        self.gr_scene.addItem(self)
        self.wrap_scene = gr_scene.scene

        self.setFlags(QGraphicsTextItem.ItemIsSelectable | QGraphicsTextItem.ItemIsMovable)
        self.setDefaultTextColor(Qt.black)
        self.setAcceptHoverEvents(True)
        self.setPos(x + 12, y - 12)
        if with_focus:
            self.into_editor()

        self._padding = 5.0
        self._radius = 5.0
        self._color_bg = QColor(color['NOTE_BG'])
        self._color_hover = QColor(color['NOTE_HOVER'])
        # brush for bg
        self._brush = QBrush()
        self._brush.setStyle(Qt.SolidPattern)
        self._brush.setColor(self._color_bg)

    def __repr__(self):
        return "<NoteItem at {}>".format(self.id)

    def is_modified(self):
        # send self modified state.
        self.gr_scene.scene.parent.send_modify_state_to_main()

    def into_editor(self):
        # call this whenever want to edit text.
        # prepare editor.
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setTextWidth(150)
        self.setFocus()

    def hoverEnterEvent(self, event):
        self._brush.setColor(self._color_hover)
        self.update()

    def hoverLeaveEvent(self, event):
        self._brush.setColor(self._color_bg)
        self.update()

    def focusOutEvent(self, event):
        if not self.toPlainText():
            debug('*[REMOVE] gotta empty note.')
            self.deleteLater()
        else:
            self.is_modified()
            self.adjustSize()  # adjust size for text
            self.setTextInteractionFlags(Qt.NoTextInteraction)
            self.wrap_scene.add_note(self)

    def mouseDoubleClickEvent(self, event):
        # double click to edit text.
        self.into_editor()

    def mouseMoveEvent(self, event):
        self.is_modified()
        super().mouseMoveEvent(event)

    def paint(self, painter, item, widget):
        rect = self.shape().boundingRect()
        new_rect = QRectF(rect.x() - self._padding / 2,
                          rect.y() - self._padding / 2,
                          rect.width() + self._padding,
                          rect.height() + self._padding)
        # painting bg
        painter.setBrush(self._brush)
        painter.drawRoundedRect(new_rect, self._radius, self._radius)
        # inherit
        super().paint(painter, item, widget)

    def serialize(self):
        return tagger(
            tag='note',
            id=self.id,
            x=str(self.x()),
            y=str(self.y()),
            content=self.toPlainText()
        )

    def deserialize(self, text):
        self.setPlainText(text)
