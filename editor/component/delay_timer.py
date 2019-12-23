from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class DelayedTimer(QObject):

    triggered = pyqtSignal(str)

    def __init__(self, parent=None, max_delay=2000, min_delay=500):
        super().__init__(parent)
        self.max_delay = max_delay
        self.min_delay = min_delay
        self.min_timer = QTimer(self)
        self.max_timer = QTimer(self)
        self.min_timer.timeout.connect(self.timeout)
        self.max_timer.timeout.connect(self.timeout)
        self.string: str = ""

    def timeout(self):
        self.min_timer.stop()
        self.max_timer.stop()
        self.triggered.emit(self.string)

    def trigger(self, p_str: str):
        self.string = p_str
        if not self.max_timer.isActive():
            self.max_timer.start(self.max_delay)
        self.min_timer.stop()
        self.min_timer.start(self.min_delay)
