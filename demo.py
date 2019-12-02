import sys
import cgitb

from PyQt5.QtWidgets import QApplication, QSplashScreen, qApp
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from cfg import icon, SS_COMMON
from lib import load_stylesheet
from editor.main import KMBMainWindow

cgitb.enable(format("text"))


def demo_run():
    app = QApplication(sys.argv)
    # get screen size.
    desktop = QApplication.desktop().screenGeometry()
    ratio = QApplication.desktop().screen().devicePixelRatio()
    width = desktop.width()
    height = desktop.height()
    # setting up welcome screen.
    screen = QPixmap(icon["SCREEN"])
    screen.setDevicePixelRatio(ratio)
    if ratio == 2:
        # under Mac Retina
        screen = screen.scaled(height * 0.9, height * 0.9)
    else:
        # under Windows and Linux
        screen = screen.scaled(height * 0.5, height * 0.5)
    splash = QSplashScreen(screen)
    splash.show()
    # handle the main process event.
    qApp.processEvents()
    # setting up main window.
    size = (width * 0.8, height * 0.8)
    editor = KMBMainWindow(size)
    stylesheet = load_stylesheet(SS_COMMON)
    app.setStyleSheet(stylesheet)
    # Mac: set the icon in dock.
    app.setWindowIcon(editor.win_icon)
    # compatible with Mac Retina screen.
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # editor show up
    editor.show()
    splash.finish(editor)
    sys.exit(app.exec_())


if __name__ == '__main__':
    demo_run()
