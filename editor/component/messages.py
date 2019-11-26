from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap, QIcon

from cfg import icon


class PopMessageBox(QMessageBox):
    """ Popup message box. """

    TYPE_OK = 0
    TYPE_ALERT = 2
    TYPE_YES_OR_NO = 4
    TYPE_SAVE_OR_NOT = 8
    TYPE_EXPORT_ERROR = 16
    TYPE_EXPORT_WARNING = 32

    def __init__(self, title: str, parent=None, run=False):
        super().__init__(parent)

        self.title = title
        self.run = run  # it will run after making.
        # icons
        self.win_icon = QIcon(icon['WINICON'])
        self.alert_icon = QPixmap(icon['ALERT'])
        self.quest_icon = QPixmap(icon['QUESTION'])
        self.ok_icon = QPixmap(icon['EXPORT_OK'])
        self.error_icon = QPixmap(icon['EXPORT_ERR'])
        # init basic ui
        self.setWindowTitle(self.title)
        self.setWindowIcon(self.win_icon)

    def make(self,
             text: str,
             pop_message_type=TYPE_ALERT,
             extra_text: str = None):
        # make one message box.
        if pop_message_type == self.TYPE_OK:
            self._make_ok()
        elif pop_message_type == self.TYPE_ALERT:
            self._make_alert()
        elif pop_message_type == self.TYPE_YES_OR_NO:
            self._make_yes_or_no()
        elif pop_message_type == self.TYPE_SAVE_OR_NOT:
            self._make_save_or_not()
        elif pop_message_type == self.TYPE_EXPORT_ERROR:
            self._make_export_error()
        elif pop_message_type == self.TYPE_EXPORT_WARNING:
            self._make_export_warning()
        else:  # default will be ALERT type.
            self._make_alert()
        # common settings
        self.setText(text)
        self.setDetailedText(extra_text)
        if self.run:  # run immediately.
            self.exec()

    def _make_ok(self):
        self.setIconPixmap(self.ok_icon)
        self.setStandardButtons(QMessageBox.Ok)

    def _make_alert(self):
        self.setIconPixmap(self.alert_icon)
        self.setStandardButtons(QMessageBox.Close)
        self.setInformativeText('<i>Press Close to return.</i>')

    def _make_yes_or_no(self):
        self.setIconPixmap(self.quest_icon)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Yes)

    def _make_save_or_not(self):
        self.setIconPixmap(self.quest_icon)
        self.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Save)

    def _make_export_error(self):
        self.setIconPixmap(self.error_icon)
        self.setStandardButtons(QMessageBox.Close)
        self.setInformativeText('<i>Please fix then retry.</i>')

    def _make_export_warning(self):
        self.setIconPixmap(self.alert_icon)
        self.setStandardButtons(QMessageBox.Close)
        self.setInformativeText('<i>Press Details to see more.</i>')
