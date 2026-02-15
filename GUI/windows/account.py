from __future__ import annotations
from typing import TYPE_CHECKING
import os

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QComboBox, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from project_configuration import AVAILABLE_LANGUAGES, FLAGS_DIRECTORY
from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER, ALIGN_V_CENTER, BASIC_FONT

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.horizontal_scroll_area import HorizontalScrollArea
from DesktopQtToolkit.default_drop_shadow_effect import DefaultDropShadowEffect


if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow




class AddAccountWindow(SubWindow):
    """Represents Add account window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.languages = QComboBox()
        self.languages.setFont(BASIC_FONT)
        self.languages.addItems(AVAILABLE_LANGUAGES)

        for language in range(len(AVAILABLE_LANGUAGES)):
            self.languages.setItemIcon(language, QIcon(os.path.join(FLAGS_DIRECTORY, f"{language}-flag.png")))

        self.languages_layout = QHBoxLayout()
        self.languages_layout.addWidget(self.languages, alignment=ALIGNMENT.AlignRight)

        self.message = QLabel()
        self.message.setFont(BASIC_FONT)
        self.message.setWordWrap(True)
        self.message.setMinimumHeight(80)
        self.message.setMinimumWidth(450)

        self.account_name = QLineEdit()
        self.account_name.setPlaceholderText("Account Name")

        self.account_name_layout = QHBoxLayout()
        self.account_name_layout.addWidget(self.account_name, alignment=ALIGNMENT.AlignCenter )

        self.button = create_button("", (140,50))
        self.button.setDefault(True)

        self.current_balance = QLineEdit()
        self.current_balance.setPlaceholderText("Current balance")

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addLayout(self.languages_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.message,alignment=ALIGN_H_CENTER)    
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.account_name_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.current_balance,alignment=ALIGN_H_CENTER)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.button,alignment=ALIGN_H_CENTER)
        self.main_layout.addStretch(1)
        self.main_layout.setContentsMargins(50, 10, 50, 30)

        self.window_container.setLayout(self.main_layout)
        self.account_name.setFocus()



class RenameAccountWindow(SubWindow):
    """Represents Rename account window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)
        
        self.message = QLabel()
        self.message.setFont(BASIC_FONT)

        self.new_account_name = QLineEdit()
        self.account_name_layout = QHBoxLayout()
        self.account_name_layout.addWidget(self.new_account_name,alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)

        self.button = create_button("Update", (160,40))
        self.button.setDefault(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.message, alignment=ALIGN_H_CENTER)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.account_name_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.button, alignment=ALIGN_H_CENTER)
        self.main_layout.addStretch(1)
        self.main_layout.setContentsMargins(50, 10, 50, 30)

        self.window_container.setLayout(self.main_layout)
        self.new_account_name.setFocus()



class SwitchAccountWindow(SubWindow):
    """Represents Switch account window structure."""

    class AccountSwitchWidget():
        """
        This class is used to create a widget that displays the account name, balance,
        and creation date and a button to switch to that account.
        """

        def __init__(self) -> None:
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
            self.account_widget.setGraphicsEffect(DefaultDropShadowEffect(self.account_widget))

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.account_switch_widgets:list[SwitchAccountWindow.AccountSwitchWidget] = []
        
        self.accounts_layout = QHBoxLayout()
        self.accounts_layout.setSpacing(50)

        self.accounts_wrapper = QWidget()
        self.accounts_wrapper.setLayout(self.accounts_layout)

        self.accounts_scroll_area = HorizontalScrollArea()
        self.accounts_scroll_area.setWidgetResizable(True)
        self.accounts_scroll_area.setStyleSheet("QScrollArea{border:none;background-color:transparent;}")
        self.accounts_scroll_area.setWidget(self.accounts_wrapper)
        self.accounts_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.accounts_scroll_area.setMinimumSize(800, 220)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.accounts_scroll_area)
        
        self.window_container.setLayout(self.main_layout)