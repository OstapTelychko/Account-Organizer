from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication
from PySide6.QtCore import Qt
from time import sleep

from GUI.gui_constants import ALIGNMENT, APP_ICON, BASIC_FONT
from GUI.windows.category import CategorySettingsWindow
from GUI.windows.statistics import MonthlyStatistics, QuarterlyStatistics, YearlyStatistics, CustomRangeStatisticsView




class InformationMessage:
    window = QWidget()
    window.setWindowFlags( Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint | Qt.WindowType.Popup)
    window.resize(250,50)
    window.setMaximumWidth(250)
    window.setMaximumHeight(50)
    window.setWindowIcon(APP_ICON)
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    message = QWidget()
    message.setProperty("class", "information_message")
    message.resize(250,50)

    message_text = QLabel("Statisctics has been copied")
    message_text.setFont(BASIC_FONT)
    message_layout = QHBoxLayout()
    message_layout.addWidget(message_text,alignment=ALIGNMENT.AlignCenter)
    message.setLayout(message_layout)

    main_layout=  QVBoxLayout()
    main_layout.addWidget(message)
    window.setLayout(main_layout)


    def run():
        """This method is used to show the information message window and center it on the main window."""

        opacity = 0
        InformationMessage.window.setWindowOpacity(0)
        InformationMessage.window.show()

        for _ in range(5):
            opacity += 0.2
            InformationMessage.window.setWindowOpacity(opacity)
            InformationMessage.window.update()
            QApplication.processEvents()
            sleep(0.05)
        sleep(0.6)
        for _ in range(5):
            opacity -= 0.2
            InformationMessage.window.setWindowOpacity(opacity)
            InformationMessage.window.update()
            QApplication.processEvents()
            sleep(0.05)

        InformationMessage.window.hide()
        CategorySettingsWindow.copy_transactions.setEnabled(True)
        MonthlyStatistics.copy_statistics.setEnabled(True)
        QuarterlyStatistics.copy_statistics.setEnabled(True)
        YearlyStatistics.copy_statistics.setEnabled(True)
        CustomRangeStatisticsView.copy_statistics.setEnabled(True)
        CustomRangeStatisticsView.copy_transactions.setEnabled(True)