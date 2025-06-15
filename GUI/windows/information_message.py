from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel , QPushButton
from PySide6.QtCore import Qt, QTimer

from DesktopQtToolkit.qsingleton import QSingleton
from GUI.gui_constants import ALIGNMENT, APP_ICON, BASIC_FONT
from project_configuration import INFORMATION_MESSAGE_DURATION




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

        self.fade_in_timer = QTimer()
        self.fade_in_timer.timeout.connect(self.fade_in_step)
        self.fade_out_timer = QTimer()
        self.fade_out_timer.timeout.connect(self.fade_out_step)
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.start_fade_out)


    def run(self) -> None:
        """Show the information message with fade in/out animation."""

        # Reset opacity
        self.opacity = 0.0
        self.setWindowOpacity(0)
        self.show()
        
        self.fade_in_timer.start(50)  # 50ms interval between steps


    def fade_in_step(self) -> None:
        """Increase opacity for fade-in effect."""

        self.opacity += 0.2
        self.setWindowOpacity(self.opacity)
        self.update()
        
        if self.opacity >= 1.0:
            self.fade_in_timer.stop()
            self.display_timer.start(INFORMATION_MESSAGE_DURATION)
    

    def start_fade_out(self) -> None:
        """Start the fade-out animation after display time."""

        self.display_timer.stop()
        self.fade_out_timer.start(50)


    def fade_out_step(self) -> None:
        """Decrease opacity for fade-out effect."""

        self.opacity -= 0.2
        self.setWindowOpacity(self.opacity)
        self.update()
        
        if self.opacity <= 0:
            self.fade_out_timer.stop()
            self.hide()

            # Enable buttons after animation is complete
            for button in self.buttons:
                button.setEnabled(True)



