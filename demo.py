import sys
import cgitb

from PyQt5.QtWidgets import QApplication, QSplashScreen, qApp
from PyQt5.QtGui import QPixmap

from cfg import icon
from editor.main import KMBMainWindow
#from editor.widgets.about import AboutWidget

cgitb.enable(format("text"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # setting up welcome screen.
    screen = QPixmap(icon["SCREEN"]).scaled(640, 640)
    splash = QSplashScreen(screen)
    splash.show()
    # handle the main process event.
    qApp.processEvents()
    # setting up main window.
    desktop = QApplication.desktop().screenGeometry()
    size = (desktop.width() * 0.8,
            desktop.height() * 0.75)
    win = KMBMainWindow(size)
    # setup about panel.
    #about = AboutWidget()
    #win.action_about.triggered.connect(about.show)
    # stay one more second then close.
    splash.finish(win)
    sys.exit(app.exec_())
