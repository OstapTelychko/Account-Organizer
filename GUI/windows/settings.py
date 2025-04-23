from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QToolButton, QComboBox, QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QIcon

from project_configuration import AVAILABLE_LANGUAGES, FLAGS_DIRECTORY

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button

from GUI.gui_constants import ALIGN_H_CENTER, ALIGN_V_CENTER, ICON_SIZE, SHADOW_EFFECT_ARGUMENTS, BASIC_FONT

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow


class SettingsWindow(SubWindow):
    """Represents Settings window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.setStyleSheet("QComboBox:active,QComboBox:focus,QComboBox:disabled{border-color:transparent}")

        self.switch_themes_button = QToolButton()
        self.switch_themes_button.setIconSize(ICON_SIZE)

        self.languages = QComboBox()
        self.languages.setFont(BASIC_FONT)
        self.languages.addItems(AVAILABLE_LANGUAGES)

        for language in range(len(AVAILABLE_LANGUAGES)):
            self.languages.setItemIcon(language, QIcon(f"{FLAGS_DIRECTORY}/{language}-flag.png"))
        
        self.backup_management = create_button("Database management", (220, 50))

        self.gui_settings_wrapper_layout = QVBoxLayout()
        self.gui_settings_wrapper_layout.addWidget(self.switch_themes_button, alignment=ALIGN_H_CENTER)
        self.gui_settings_wrapper_layout.addWidget(self.languages, alignment=ALIGN_H_CENTER)
        self.gui_settings_wrapper_layout.addWidget(self.backup_management, alignment=ALIGN_H_CENTER)

        self.gui_settings_wrapper = QWidget()
        self.gui_settings_wrapper.setProperty("class", "wrapper")
        self.gui_settings_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(self.gui_settings_wrapper, **SHADOW_EFFECT_ARGUMENTS))
        self.gui_settings_wrapper.setLayout(self.gui_settings_wrapper_layout)
        self.gui_settings_wrapper.setMinimumHeight(220)
        self.gui_settings_wrapper.setMinimumWidth(250)

        self.switch_account = create_button("Switch account",(180,50))
        self.add_account = create_button("Add account",(180,50))
        self.rename_account = create_button("Rename account",(180,50))

        self.delete_account = create_button("Delete account",(180,50))
        self.delete_account.setStyleSheet("QPushButton{color:rgba(255,0,0,150); border-color:red;}")

        self.account_management_wrapper_layout = QVBoxLayout()
        self.account_management_wrapper_layout.addWidget(self.switch_account, alignment=ALIGN_H_CENTER)
        self.account_management_wrapper_layout.addWidget(self.add_account, alignment=ALIGN_H_CENTER)
        self.account_management_wrapper_layout.addWidget(self.rename_account, alignment=ALIGN_H_CENTER)
        self.account_management_wrapper_layout.addWidget(self.delete_account, alignment=ALIGN_H_CENTER)

        self.account_management_wrapper = QWidget()
        self.account_management_wrapper.setLayout(self.account_management_wrapper_layout)
        self.account_management_wrapper.setProperty("class", "wrapper")
        self.account_management_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(self.account_management_wrapper, **SHADOW_EFFECT_ARGUMENTS))

        self.total_income = QLabel()
        self.total_income.setProperty("class", "light-text")
        self.total_income.setFont(BASIC_FONT)

        self.total_expense = QLabel()
        self.total_expense.setFont(BASIC_FONT)
        self.total_expense.setProperty("class", "light-text")

        self.account_created_date = QLabel()
        self.account_created_date.setFont(BASIC_FONT)
        self.account_created_date.setProperty("class", "light-text")

        self.app_version = QLabel()
        self.app_version.setFont(BASIC_FONT)
        self.app_version.setProperty("class", "light-text")

        self.account_info_wrapper_layout = QVBoxLayout()
        self.account_info_wrapper_layout.addWidget(self.total_income, alignment=ALIGN_H_CENTER)
        self.account_info_wrapper_layout.addWidget(self.total_expense, alignment=ALIGN_H_CENTER)
        self.account_info_wrapper_layout.addWidget(self.account_created_date, alignment=ALIGN_H_CENTER)
        self.account_info_wrapper_layout.addWidget(self.app_version, alignment=ALIGN_H_CENTER)

        self.account_info_wrapper = QWidget()
        self.account_info_wrapper.setProperty("class", "wrapper")
        self.account_info_wrapper.setLayout(self.account_info_wrapper_layout)
        self.account_info_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(self.account_info_wrapper, **SHADOW_EFFECT_ARGUMENTS))

        self.gui_settings_and_account_management = QHBoxLayout()
        self.gui_settings_and_account_management.addStretch(1)
        self.gui_settings_and_account_management.addWidget(self.gui_settings_wrapper, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.gui_settings_and_account_management.addStretch(1)
        self.gui_settings_and_account_management.addWidget(self.account_management_wrapper, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.gui_settings_and_account_management.addStretch(1)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addLayout(self.gui_settings_and_account_management)
        self.main_layout.addWidget(self.account_info_wrapper, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.main_layout.addStretch(1)
        self.main_layout.setContentsMargins(50, 10, 50, 20)

        self.window_container.setLayout(self.main_layout)
