from sys import argv, platform

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor, QFont

from project_configuration import APP_NAME, ROOT_DIRECTORY


app = QApplication(argv)
app.setApplicationName(APP_NAME)


ALIGMENT = Qt.AlignmentFlag
ICON_SIZE = QSize(30, 30)
APP_ICON = QIcon(f"{ROOT_DIRECTORY}/Images/App icon.png")

SHADOW_EFFECT_ARGUMENTS = {"blurRadius":15, "xOffset":0, "yOffset":0, "color":QColor(0, 0, 0)}


if platform == "linux":
    BASIC_FONT = QFont("C059 [urw]", pointSize=12)
else:#Windows
    BASIC_FONT = QFont("Georgia", pointSize=12)