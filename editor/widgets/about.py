from PyQt5.QtWidgets import QDialog, QLabel, QApplication
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

from cfg import icon
from cfg import __version__, __author__


class AboutKMB(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        # init components.
        self.header = QLabel(self)
        self.header_img = QPixmap(icon['COVER'])
        self.body = QLabel(self)
        self.foot = QLabel(self)
        self.git_link = QLabel(self)
        self.git_img = QLabel(self)
        self.github = QPixmap(icon['GIT'])
        # init configures.
        self.width = 500
        self.height = 370
        # compatible with Mac Retina screen.
        self.ratio = QApplication.desktop().screen().devicePixelRatio()
        self.github.setDevicePixelRatio(self.ratio)
        self.font = QFont('monospace')
        # init UI.
        self.setup_ui()

    def setup_ui(self):
        # setup self ui.
        self.setFixedSize(self.width, self.height)
        self.setWindowFlag(Qt.FramelessWindowHint)
        # setup header img.
        self.header.setGeometry(0, 0, self.width, self.height // 3)
        self.header.setPixmap(self.header_img.scaled(self.width, self.width))
        # setup body context.
        self.body.setGeometry(60, 80, self.width, self.height-80)
        self.body.setFont(self.font)
        self.body.setText(
            """
            <h1>Karken: KMB {}</h1>
            Created by <b>{}</b><br>
            License under <b>GNU General Public License v3.0</b>
            <p>
            Karken: KMB(Keras Model Builder) is a software based on Keras <br>
            functional API. Build your model easily and very convenient to <br>
            generate Python code.
            </p>
            <p>
            <b>Thanks</b> to Fullzoon_(:3」ㄥ)_
            </p>
            """.format(__version__, __author__)
        )
        # setup foot context.
        self.foot.setGeometry(60, 310, self.width, 50)
        self.foot.setText("<i>Press any key to leave.</i>")
        # setup git link.
        self.git_link.setGeometry(320, 310, self.width, 50)
        self.git_link.setOpenExternalLinks(True)
        self.git_link.setText('<a href="https://github.com/ShawnHXH/Karken-KMB">'
                              'View on GitHub</a>')
        # setup icon for github.
        self.git_img.setGeometry(420, 300, 64, 64)
        self.git_img.setPixmap(self.github)

    def __call__(self, *args, **kwargs):
        self.exec()

    def keyPressEvent(self, event):
        self.close()
        super().keyPressEvent(event)
