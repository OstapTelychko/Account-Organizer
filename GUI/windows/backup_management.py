from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QHeaderView, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QSizePolicy,\
    QCheckBox, QLineEdit
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.table_widget import CustomTableWidget
from DesktopQtToolkit.default_drop_shadow_effect import DefaultDropShadowEffect

from GUI.gui_constants import BASIC_FONT, ALIGN_H_CENTER, ALIGNMENT, ALIGN_V_CENTER

from project_configuration import MAX_BACKUPS_VALIDATOR_REGEX, MAX_LEGACY_BACKUPS_VALIDATOR_REGEX

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow


class BackupManagementWindow(SubWindow):
    """Represents Backup management window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.backups_table = CustomTableWidget()
        self.backups_table.setColumnCount(3)
        self.backups_table.setMinimumSize(500, 300)
        self.backups_table.setProperty("class", "backups_table")
        self.backups_table.setColumnHidden(2, True)

        column = self.backups_table.verticalHeader()
        column.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        column.setStretchLastSection(True)

        row = self.backups_table.horizontalHeader()
        row.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        row.setFont(BASIC_FONT)

        self.create_backup = create_button("Create backup", (215, 40))
        self.delete_backup = create_button("Delete backup", (215, 40))
        self.load_backup = create_button("Restore backup", (215, 40))

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.create_backup, alignment=ALIGN_H_CENTER)
        self.buttons_layout.addWidget(self.delete_backup, alignment=ALIGN_H_CENTER)
        self.buttons_layout.addWidget(self.load_backup, alignment=ALIGN_H_CENTER)

        self.backups_layout = QVBoxLayout()
        self.backups_layout.addWidget(self.backups_table)
        self.backups_layout.addLayout(self.buttons_layout)

        self.backups_wrapper = QWidget()
        self.backups_wrapper.setProperty("class", "wrapper")
        self.backups_wrapper.setLayout(self.backups_layout)
        self.backups_wrapper.setGraphicsEffect(DefaultDropShadowEffect(self.backups_wrapper))

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.setSpacing(25)
        self.main_layout.addWidget(self.backups_wrapper)
        self.main_layout.setContentsMargins(20, 10, 20, 20)

        self.window_container.setLayout(self.main_layout)


class AutoBackupWindow(SubWindow):
    """Represents Auto backup window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.current_status = QLabel("Status: monthly")
        self.current_status.setFont(BASIC_FONT)
        self.current_status.setProperty("class", "light-text")

        self.status_wrapper = QWidget()
        self.status_wrapper.setProperty("class", "wrapper")
        self.status_wrapper.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.status_wrapper.setGraphicsEffect(DefaultDropShadowEffect(self.status_wrapper))

        self.status_wrapper_layout = QVBoxLayout()
        self.status_wrapper_layout.addWidget(self.current_status)
        self.status_wrapper_layout.setContentsMargins(20, 20, 20, 20)

        self.status_wrapper.setLayout(self.status_wrapper_layout)

        self.monthly = QCheckBox("Monthly")
        self.monthly.setFont(BASIC_FONT)
        self.monthly.setProperty("class", "light-text")

        self.weekly = QCheckBox("Weekly")
        self.weekly.setFont(BASIC_FONT)
        self.weekly.setProperty("class", "light-text")

        self.daily = QCheckBox("Daily")
        self.daily.setFont(BASIC_FONT)
        self.daily.setProperty("class", "light-text")

        self.no_auto_backup = QCheckBox("No auto backup")
        self.no_auto_backup.setFont(BASIC_FONT)
        self.no_auto_backup.setProperty("class", "light-text")
        
        self.backup_status_layout = QVBoxLayout()
        self.backup_status_layout.addWidget(self.monthly)
        self.backup_status_layout.addWidget(self.weekly)
        self.backup_status_layout.addWidget(self.daily)
        self.backup_status_layout.addWidget(self.no_auto_backup)
        
        self.auto_backup_status_wrapper = QWidget()
        self.auto_backup_status_wrapper.setProperty("class", "wrapper")
        self.auto_backup_status_wrapper.setLayout(self.backup_status_layout)
        self.auto_backup_status_wrapper.setGraphicsEffect(DefaultDropShadowEffect(self.auto_backup_status_wrapper))

        self.status_and_auto_backup_layout = QVBoxLayout()
        self.status_and_auto_backup_layout.addWidget(self.status_wrapper, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER, stretch=10)
        self.status_and_auto_backup_layout.addWidget(self.auto_backup_status_wrapper, alignment=ALIGNMENT.AlignTop, stretch=90)

        self.max_backups = QLineEdit()
        self.max_backups.setMinimumWidth(220)
        max_backups_validator = QRegularExpressionValidator(QRegularExpression(MAX_BACKUPS_VALIDATOR_REGEX))
        self.max_backups.setValidator(max_backups_validator)

        self.max_backups_label = QLabel("Max backups")
        self.max_backups_label.setMinimumSize(450, 150)
        self.max_backups_label.setWordWrap(True)
        self.max_backups_label.setFont(BASIC_FONT)
        self.max_backups_label.setProperty("class", "light-text")

        self.max_legacy_backups = QLineEdit()
        self.max_legacy_backups.setMinimumWidth(250)
        max_legacy_backups_validator = QRegularExpressionValidator(QRegularExpression(MAX_LEGACY_BACKUPS_VALIDATOR_REGEX))
        self.max_legacy_backups.setValidator(max_legacy_backups_validator)

        self.max_legacy_backups_label = QLabel("Max legacy backups")
        self.max_legacy_backups_label.setMinimumSize(450, 150)
        self.max_legacy_backups_label.setWordWrap(True)
        self.max_legacy_backups_label.setFont(BASIC_FONT)
        self.max_legacy_backups_label.setProperty("class", "light-text")

        self.no_auto_removal = QCheckBox("No auto removal")
        self.no_auto_removal.setFont(BASIC_FONT)
        self.no_auto_removal.setProperty("class", "light-text")

        self.max_backups_layout = QVBoxLayout()
        self.max_backups_layout.setContentsMargins(10, 0, 10, 10)
        self.max_backups_layout.addWidget(self.max_backups_label, alignment=ALIGN_H_CENTER)
        self.max_backups_layout.addWidget(self.max_backups, alignment=ALIGN_H_CENTER)
        self.max_backups_layout.addWidget(self.max_legacy_backups_label, alignment=ALIGN_H_CENTER)
        self.max_backups_layout.addWidget(self.max_legacy_backups, alignment=ALIGN_H_CENTER)
        self.max_backups_layout.addSpacing(30)
        self.max_backups_layout.addWidget(self.no_auto_removal, alignment=ALIGN_H_CENTER)

        self.max_backups_wrapper = QWidget()
        self.max_backups_wrapper.setProperty("class", "wrapper")
        self.max_backups_wrapper.setLayout(self.max_backups_layout)
        self.max_backups_wrapper.setGraphicsEffect(DefaultDropShadowEffect(self.max_backups_wrapper))

        self.status_and_max_backup_layout = QHBoxLayout()
        self.status_and_max_backup_layout.addLayout(self.status_and_auto_backup_layout)
        self.status_and_max_backup_layout.addWidget(self.max_backups_wrapper)

        self.save = create_button("Save", (100, 40))
        self.save.setFont(BASIC_FONT)
        self.save.setDefault(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.setSpacing(25)
        self.main_layout.addLayout(self.status_and_max_backup_layout)
        self.main_layout.addWidget(self.save, alignment=ALIGN_H_CENTER)
        self.main_layout.setContentsMargins(20, 10, 20, 20)

        self.window_container.setLayout(self.main_layout)
        self.max_backups.setFocus()