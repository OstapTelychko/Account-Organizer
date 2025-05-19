from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QPushButton
from PySide6.QtCore import Qt
from time import sleep

from DesktopQtToolkit.qsingleton import QSingleton
from GUI.gui_constants import ALIGNMENT, APP_ICON, BASIC_FONT




class InformationMessage(QWidget, metaclass=QSingleton):
    """Represents information message window structure."""

    singleton_message = "Cannot create multiple instances of InformationMessage class. Use WindowsRegistry instead."

    def __init__(self, buttons:list[QPushButton]) -> None:
        """Initialize the information message window with buttons.

            Arguments
            ---------
            `buttons` : list[QPushButton] - list of buttons to be enabled after the message is shown.
        """

        super().__init__()
        self.buttons = buttons

        self.setWindowFlags( Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint | Qt.WindowType.Popup)
        self.resize(250,50)
        self.setMaximumWidth(250)
        self.setMaximumHeight(50)
        self.setWindowIcon(APP_ICON)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.message = QWidget()
        self.message.setProperty("class", "information_message")
        self.message.resize(250,50)

        self.message_text = QLabel("Statistics has been copied")
        self.message_text.setFont(BASIC_FONT)
        self.message_layout = QHBoxLayout()
        self.message_layout.addWidget(self.message_text,alignment=ALIGNMENT.AlignCenter)
        self.message.setLayout(self.message_layout)

        self.main_layout=  QVBoxLayout()
        self.main_layout.addWidget(self.message)
        self.setLayout(self.main_layout)


    def run(self) -> None:
        """This method is used to show the information message window and center it on the main window."""

        opacity = 0.0
        self.setWindowOpacity(0)
        self.show()

        for _ in range(5):
            opacity += 0.2
            self.setWindowOpacity(opacity)
            self.update()
            QApplication.processEvents()
            sleep(0.05)

        sleep(0.6)
        
        for _ in range(5):
            opacity -= 0.2
            self.setWindowOpacity(opacity)
            self.update()
            QApplication.processEvents()
            sleep(0.05)

        self.hide()
        for button in self.buttons:
            button.setEnabled(True)



