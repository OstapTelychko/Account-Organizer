import os
from sys import argv, platform

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor, QFont, QFontDatabase

from project_configuration import APP_NAME, GENERAL_ICONS_DIRECTORY, REGULAR_FONT_PATH, BOLD_FONT_PATH


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


regular_id = QFontDatabase.addApplicationFont(REGULAR_FONT_PATH)
bold_id = QFontDatabase.addApplicationFont(BOLD_FONT_PATH)
if regular_id != -1 and bold_id != -1:
    font_family = QFontDatabase.applicationFontFamilies(regular_id)[0]
    BASIC_FONT = QFont(font_family, pointSize=12)
    BIG_BASIC_FONT = QFont(font_family, pointSize=15)
else:
    if platform == "linux":
        BASIC_FONT = QFont("C059 [urw]", pointSize=12)
        BIG_BASIC_FONT = QFont("C059 [urw]", pointSize=15)
    else:#Windows
        BASIC_FONT = QFont("Georgia", pointSize=12)
        BIG_BASIC_FONT = QFont("Georgia", pointSize=15)