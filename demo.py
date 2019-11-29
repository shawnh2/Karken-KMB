import sys
import cgitb

from PyQt5.QtWidgets import QApplication, QSplashScreen, qApp
from PyQt5.QtGui import QPixmap

from cfg import icon, SS_COMMON
from lib import load_stylesheet
from editor.main import KMBMainWindow

cgitb.enable(format("text"))


def demo_run():
    app = QApplication(sys.argv)
    # get screen size.
    desktop = QApplication.desktop().screenGeometry()
    width = desktop.width()
    height = desktop.height()
    # setting up welcome screen.
    screen = QPixmap(icon["SCREEN"]).scaled(height * 0.5, height * 0.5)
    splash = QSplashScreen(screen)
    splash.show()
    # handle the main process event.
    qApp.processEvents()
    # setting up main window.
    size = (width * 0.8, height * 0.8)
    win = KMBMainWindow(size)
    stylesheet = load_stylesheet(SS_COMMON)
    app.setStyleSheet(stylesheet)
    win.show()
    # stay one more second then close.
    splash.finish(win)
    sys.exit(app.exec_())


if __name__ == '__main__':
    demo_run()
