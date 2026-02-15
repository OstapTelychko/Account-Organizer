from __future__ import annotations
import os

from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QToolButton, QComboBox, QLabel, QVBoxLayout, QGridLayout
from PySide6.QtGui import QIcon

from project_configuration import AVAILABLE_LANGUAGES, FLAGS_DIRECTORY

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.default_drop_shadow_effect import DefaultDropShadowEffect

from GUI.gui_constants import ALIGN_H_CENTER, ALIGN_V_CENTER, ICON_SIZE, BASIC_FONT

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow


class SettingsWindow(SubWindow):
    """Represents Settings window structure."""

    class SettingsSection(QWidget):
        
        def __init__(self) -> None:
            super().__init__()

            self.section_name = QLabel()
            self.section_name.setProperty("class", "light-text")
            self.section_name.setFont(BASIC_FONT)

            self.section_layout = QVBoxLayout()
            self.section_layout.addWidget(self.section_name, alignment=ALIGN_H_CENTER)

            self.section_wrapper = QWidget()
            self.section_wrapper.setProperty("class", "wrapper")
            self.section_wrapper.setGraphicsEffect(
                DefaultDropShadowEffect(self.section_wrapper)
            )
            self.section_wrapper.setLayout(self.section_layout)



    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.setStyleSheet("QComboBox:active,QComboBox:focus,QComboBox:disabled{border-color:transparent}")

        self.switch_themes_button = QToolButton()
        self.switch_themes_button.setIconSize(ICON_SIZE)

        self.languages = QComboBox()
        self.languages.setFont(BASIC_FONT)
        self.languages.addItems(AVAILABLE_LANGUAGES)

        for language in range(len(AVAILABLE_LANGUAGES)):
            self.languages.setItemIcon(language, QIcon(os.path.join(FLAGS_DIRECTORY, f"{language}-flag.png")))

        self.shortcuts_management = create_button("Shortcuts management", (220, 50))
        
        self.general_section = self.SettingsSection()
        self.general_section.section_layout.addWidget(self.switch_themes_button, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.general_section.section_layout.addWidget(self.languages, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.general_section.section_layout.addWidget(self.shortcuts_management, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)

        self.switch_account = create_button("Switch account",(180,50))
        self.add_account = create_button("Add account",(180,50))
        self.rename_account = create_button("Rename account",(180,50))

        self.delete_account = create_button("Delete account",(180,50))
        self.delete_account.setStyleSheet("QPushButton{color:rgba(255,0,0,150); border-color:red;}")

        self.account_section = self.SettingsSection()
        self.account_section.section_layout.addWidget(self.switch_account, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.account_section.section_layout.addWidget(self.add_account, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.account_section.section_layout.addWidget(self.rename_account, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.account_section.section_layout.addWidget(self.delete_account, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)

        self.backup_management = create_button("Database management", (220, 50))
        self.auto_backup = create_button("Auto backup", (220, 40))
        self.auto_backup_status = QLabel("Status monthly")
        self.auto_backup_status.setProperty("class", "light-text")
        self.auto_backup_status.setFont(BASIC_FONT)

        self.backup_section = self.SettingsSection()
        self.backup_section.section_layout.addWidget(self.backup_management, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.backup_section.section_layout.addWidget(self.auto_backup, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.backup_section.section_layout.addWidget(self.auto_backup_status, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)

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

        self.account_info_section = self.SettingsSection()
        self.account_info_section.section_layout.addWidget(self.total_income, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.account_info_section.section_layout.addWidget(self.total_expense, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.account_info_section.section_layout.addWidget(self.account_created_date, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.account_info_section.section_layout.addWidget(self.app_version, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)

        self.general_section.section_wrapper.setMinimumSize(320, 265)
        self.account_section.section_wrapper.setMinimumSize(320, 265)
        self.backup_section.section_wrapper.setMinimumSize(320, 265)
        self.account_info_section.section_wrapper.setMinimumSize(320, 265)

        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.addLayout(self.window_menu_layout, 0, 0, 1, 2, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.main_layout.addWidget(self.general_section.section_wrapper, 1, 0, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.main_layout.addWidget(self.account_section.section_wrapper, 1, 1, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.main_layout.addWidget(self.backup_section.section_wrapper, 2, 0, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.main_layout.addWidget(self.account_info_section.section_wrapper, 2, 1, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.main_layout.setContentsMargins(50, 10, 50, 20)

        self.window_container.setLayout(self.main_layout)
