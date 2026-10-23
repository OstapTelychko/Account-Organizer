from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel , QPushButton
from PySide6.QtCore import Qt, QTimer

from DesktopQtToolkit.qsingleton import QSingleton
from GUI.gui_constants import ALIGNMENT, APP_ICON, BASIC_FONT
from project_configuration import INFORMATION_MESSAGE_DURATION, INFORMATION_MESSAGE_STEP_INTERVAL,\
    INFORMATION_MESSAGE_STEPS


INFORMATION_MESSAGE_MIN_WIDTH = 250
INFORMATION_MESSAGE_LINE_HEIGHT = 50
INFORMATION_MESSAGE_EXTRA_LINE_HEIGHT = 30
INFORMATION_MESSAGE_HORIZONTAL_PADDING = 60



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

        # Tool tip windows don't grab input like popups, so shortcuts and clicks keep working while it's shown
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
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
        self.message_text.setAlignment(ALIGNMENT.AlignCenter)
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
        self.opacity_step = 1.0 / INFORMATION_MESSAGE_STEPS


    def run(self) -> None:
        """Show the information message with fade in/out animation. The message is resized to fit long or multi-line text."""

        lines_amount = self.message_text.text().count("\n") + 1
        width = max(
            INFORMATION_MESSAGE_MIN_WIDTH,
            self.message_text.sizeHint().width() + INFORMATION_MESSAGE_HORIZONTAL_PADDING
        )
        height = INFORMATION_MESSAGE_LINE_HEIGHT + INFORMATION_MESSAGE_EXTRA_LINE_HEIGHT * (lines_amount - 1)
        self.setMaximumSize(width, height)
        self.resize(width, height)

        # Reset opacity
        self.opacity = 0.0
        self.setWindowOpacity(0)
        self.show()
        
        self.fade_in_timer.start(INFORMATION_MESSAGE_STEP_INTERVAL)


    def fade_in_step(self) -> None:
        """Increase opacity for fade-in effect."""

        self.opacity += self.opacity_step
        self.setWindowOpacity(self.opacity)
        self.update()
        
        if self.opacity >= 1.0:
            self.fade_in_timer.stop()
            self.display_timer.start(INFORMATION_MESSAGE_DURATION)
    

    def start_fade_out(self) -> None:
        """Start the fade-out animation after display time."""

        self.display_timer.stop()
        self.fade_out_timer.start(INFORMATION_MESSAGE_STEP_INTERVAL)


    def fade_out_step(self) -> None:
        """Decrease opacity for fade-out effect."""

        self.opacity -= self.opacity_step
        self.setWindowOpacity(self.opacity)
        self.update()
        
        if self.opacity <= 0:
            self.fade_out_timer.stop()
            self.hide()

            # Enable buttons after animation is complete
            for button in self.buttons:
                button.setEnabled(True)



