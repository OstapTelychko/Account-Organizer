from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QComboBox, QScrollArea, QWidget, QGraphicsDropShadowEffect
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from project_configuration import AVAILABLE_LANGUAGES, FLAGS_DIRECTORY

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.horizontal_scroll_area import HorizontalScrollArea

from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER, ALIGN_V_CENTER, BASIC_FONT, SHADOW_EFFECT_ARGUMENTS
from GUI.windows.main_window import MainWindow



class AddAccountWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    languages = QComboBox()
    languages.setFont(BASIC_FONT)
    languages.addItems(AVAILABLE_LANGUAGES)

    for language in range(len(AVAILABLE_LANGUAGES)):
        languages.setItemIcon(language, QIcon(f"{FLAGS_DIRECTORY}/{language}-flag.png"))

    languages_layout = QHBoxLayout()
    languages_layout.addWidget(languages, alignment=ALIGNMENT.AlignRight)

    message = QLabel()
    message.setFont(BASIC_FONT)
    message.setWordWrap(True)
    message.setMinimumHeight(80)
    message.setMinimumWidth(450)

    account_name = QLineEdit()
    account_name.setPlaceholderText("Account Name")

    account_name_layout = QHBoxLayout()
    account_name_layout.addWidget(account_name, alignment=ALIGNMENT.AlignCenter )

    button = create_button("", (140,50))
    button.setDefault(True)

    current_balance = QLineEdit()
    current_balance.setPlaceholderText("Current balance")

    main_layout = QVBoxLayout()
    main_layout.setSpacing(20)
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addLayout(languages_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(message,alignment=ALIGN_H_CENTER)    
    main_layout.addStretch(1)
    main_layout.addLayout(account_name_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(current_balance,alignment=ALIGN_H_CENTER)
    main_layout.addStretch(1)
    main_layout.addWidget(button,alignment=ALIGN_H_CENTER)
    main_layout.addStretch(1)
    main_layout.setContentsMargins(50, 10, 50, 30)

    window.window_container.setLayout(main_layout)



class RenameAccountWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)
    
    message = QLabel()
    message.setFont(BASIC_FONT)

    new_account_name = QLineEdit()
    account_name_layout = QHBoxLayout()
    account_name_layout.addWidget(new_account_name,alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)

    button = create_button("Update", (160,40))
    button.setDefault(True)

    main_layout = QVBoxLayout()
    main_layout.setSpacing(20)
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(message, alignment=ALIGN_H_CENTER)
    main_layout.addStretch(1)
    main_layout.addLayout(account_name_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(button, alignment=ALIGN_H_CENTER)
    main_layout.addStretch(1)
    main_layout.setContentsMargins(50, 10, 50, 30)

    window.window_container.setLayout(main_layout)



class SwitchAccountWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    accounts_layout = QHBoxLayout()
    accounts_layout.setSpacing(50)

    class AccountSwitchWidget():
        """This class is used to create a widget that displays the account name, balance, and creation date and a button to switch to that account."""

        def __init__(self):
            self.account_name_label = QLabel()
            self.account_name_label.setFont(BASIC_FONT)
            self.account_name_label.setAlignment(ALIGN_H_CENTER)
            self.account_name_label.setProperty("class", "light-text")

            self.account_balance_label = QLabel(f"Balance: 0")
            self.account_balance_label.setFont(BASIC_FONT)
            self.account_balance_label.setAlignment(ALIGN_H_CENTER)
            self.account_balance_label.setProperty("class", "light-text")

            self.account_creation_date_label = QLabel("Creation date: 2023-04-01")
            self.account_creation_date_label.setFont(BASIC_FONT)
            self.account_creation_date_label.setAlignment(ALIGN_H_CENTER)
            self.account_creation_date_label.setProperty("class", "light-text")

            self.switch_button = create_button("Switch", (120,40))
            self.switch_button.setDefault(True)

            self.account_layout = QVBoxLayout()
            self.account_layout.setSpacing(10)
            self.account_layout.addWidget(self.account_name_label)
            self.account_layout.addWidget(self.account_balance_label)
            self.account_layout.addWidget(self.account_creation_date_label)
            self.account_layout.addWidget(self.switch_button, alignment=ALIGN_H_CENTER)
            self.account_layout.addStretch(1)

            self.account_widget = QWidget()
            self.account_widget.setLayout(self.account_layout)
            self.account_widget.setProperty("class", "wrapper")
            self.account_widget.setGraphicsEffect(QGraphicsDropShadowEffect(self.account_widget, **SHADOW_EFFECT_ARGUMENTS))

    accounts_wrapper = QWidget()
    accounts_wrapper.setLayout(accounts_layout)

    accounts_scroll_area = HorizontalScrollArea()
    accounts_scroll_area.setWidgetResizable(True)
    accounts_scroll_area.setStyleSheet("QScrollArea{border:none;background-color:transparent;}")
    accounts_scroll_area.setWidget(accounts_wrapper)
    accounts_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    accounts_scroll_area.setMinimumSize(400, 220)

    main_layout = QVBoxLayout()
    main_layout.setSpacing(20)
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addWidget(accounts_scroll_area)
    
    window.window_container.setLayout(main_layout)