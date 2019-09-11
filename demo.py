import sys
import cgitb

from PyQt5.QtWidgets import QApplication

from editor import KMBMainWindow

cgitb.enable(format("text"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = KMBMainWindow()
    sys.exit(app.exec_())
