import sys
import time
import cgitb

from PyQt5.QtWidgets import QApplication, QSplashScreen, qApp
from PyQt5.QtGui import QPixmap

from editor.main import KMBMainWindow

cgitb.enable(format("text"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # setting up welcome screen.
    #screen = QPixmap('lib/screen/keras.png')
    #splash = QSplashScreen(screen)
    #splash.show()
    # handle the main process event.
    #qApp.processEvents()
    # setting up main window.
    win = KMBMainWindow()
    # stay one more second then close.
    #time.sleep(1)
    #splash.finish(win)
    sys.exit(app.exec_())
