import os
from sys import argv, platform

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor, QFont

from project_configuration import APP_NAME, GENERAL_ICONS_DIRECTORY


app = QApplication(argv)
app.setApplicationName(APP_NAME)

DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Attribute for dark mode

ALIGNMENT = Qt.AlignmentFlag
ALIGN_H_CENTER = ALIGNMENT.AlignHCenter
ALIGN_V_CENTER = ALIGNMENT.AlignVCenter

ICON_SIZE = QSize(30, 30)

if platform == "linux":
    APP_ICON = QIcon(os.path.join(GENERAL_ICONS_DIRECTORY, "App icon.png"))
else:
    APP_ICON = QIcon(os.path.join(GENERAL_ICONS_DIRECTORY, "App icon.ico"))
app.setWindowIcon(APP_ICON)

APP_UPGRADE_ICON = QIcon(os.path.join(GENERAL_ICONS_DIRECTORY, "App upgrade icon.svg")).pixmap(64, 64)
NO_INTERNET_ICON = QIcon(os.path.join(GENERAL_ICONS_DIRECTORY, "no internet connection.png")).pixmap(64, 64)

SHADOW_EFFECT_ARGUMENTS = {"blurRadius":15, "xOffset":0, "yOffset":0, "color":QColor(0, 0, 0)}
FOCUSED_SHADOW_EFFECT_ARGUMENTS = {"blurRadius":20, "xOffset":0, "yOffset":0, "color":QColor(70, 120, 255)}

if platform == "linux":
    BASIC_FONT = QFont("C059 [urw]", pointSize=12)
    BIG_BASIC_FONT = QFont("C059 [urw]", pointSize=15)
else:#Windows
    BASIC_FONT = QFont("Georgia", pointSize=12)
    BIG_BASIC_FONT = QFont("Georgia", pointSize=15)