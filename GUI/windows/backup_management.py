from PySide6.QtWidgets import QHeaderView, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QSizePolicy, QGraphicsDropShadowEffect, QCheckBox, QLineEdit
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.table_widget import CustomTableWidget

from GUI.windows.main_window import MainWindow
from GUI.gui_constants import BASIC_FONT, ALIGN_H_CENTER, SHADOW_EFFECT_ARGUMENTS, ALIGNMENT, ALIGN_V_CENTER

from project_configuration import MAX_BACKUPS_VALIDATOR_REGEX, MAX_LEGACY_BACKUPS_VALIDATOR_REGEX



class BackupManagementWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    backups_table = CustomTableWidget()
    backups_table.setColumnCount(3)
    backups_table.setMinimumSize(500, 300)
    backups_table.setProperty("class", "backups_table")
    backups_table.setColumnHidden(2, True)

    column = backups_table.verticalHeader()
    column.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    row = backups_table.horizontalHeader()
    row.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    row.setFont(BASIC_FONT)

    create_backup = create_button("Create backup", (215, 40))
    delete_backup = create_button("Delete backup", (215, 40))
    load_backup = create_button("Restore backup", (215, 40))

    buttons_layout = QHBoxLayout()
    buttons_layout.addWidget(create_backup, alignment=ALIGN_H_CENTER)
    buttons_layout.addWidget(delete_backup, alignment=ALIGN_H_CENTER)
    buttons_layout.addWidget(load_backup, alignment=ALIGN_H_CENTER)

    backups_layout = QVBoxLayout()
    backups_layout.addWidget(backups_table)
    backups_layout.addLayout(buttons_layout)

    backups_wrapper = QWidget()
    backups_wrapper.setProperty("class", "wrapper")
    backups_wrapper.setLayout(backups_layout)
    backups_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(backups_wrapper, **SHADOW_EFFECT_ARGUMENTS))

    auto_backup = create_button("Auto backup", (220, 40))
    auto_backup_status = QLabel("Status monthly")
    auto_backup_status.setProperty("class", "light-text")
    auto_backup_status.setFont(BASIC_FONT)

    auto_backup_layout = QVBoxLayout()
    auto_backup_layout.addWidget(auto_backup, alignment=ALIGN_H_CENTER)
    auto_backup_layout.addWidget(auto_backup_status, alignment=ALIGN_H_CENTER)

    auto_backup_wrapper = QWidget()
    auto_backup_wrapper.setProperty("class", "wrapper")
    auto_backup_wrapper.setLayout(auto_backup_layout)
    auto_backup_wrapper.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
    auto_backup_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(auto_backup_wrapper, **SHADOW_EFFECT_ARGUMENTS))

    main_layout = QVBoxLayout()
    main_layout.addLayout(window.window_menu_layout)
    main_layout.setSpacing(25)
    main_layout.addWidget(backups_wrapper)
    main_layout.addWidget(auto_backup_wrapper, alignment=ALIGN_H_CENTER)
    main_layout.setContentsMargins(20, 10, 20, 20)

    window.window_container.setLayout(main_layout)



class AutoBackupWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    current_status = QLabel("Status: monthly")
    current_status.setFont(BASIC_FONT)
    current_status.setProperty("class", "light-text")

    status_wrapper = QWidget()
    status_wrapper.setProperty("class", "wrapper")
    status_wrapper.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
    status_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(status_wrapper, **SHADOW_EFFECT_ARGUMENTS))

    status_wrapper.setLayout(QVBoxLayout())
    status_wrapper.layout().addWidget(current_status, alignment=ALIGN_H_CENTER)
    status_wrapper.layout().setContentsMargins(20, 20, 20, 20)

    monthly = QCheckBox("Monthly")
    monthly.setFont(BASIC_FONT)
    monthly.setProperty("class", "light-text")

    weekly = QCheckBox("Weekly")
    weekly.setFont(BASIC_FONT)
    weekly.setProperty("class", "light-text")

    daily = QCheckBox("Daily")
    daily.setFont(BASIC_FONT)
    daily.setProperty("class", "light-text")

    no_auto_backup = QCheckBox("No auto backup")
    no_auto_backup.setFont(BASIC_FONT)
    no_auto_backup.setProperty("class", "light-text")
    
    backup_status_layout = QVBoxLayout()
    backup_status_layout.addWidget(monthly)
    backup_status_layout.addWidget(weekly)
    backup_status_layout.addWidget(daily)
    backup_status_layout.addWidget(no_auto_backup)
    
    auto_backup_status_wrapper = QWidget()
    auto_backup_status_wrapper.setProperty("class", "wrapper")
    auto_backup_status_wrapper.setLayout(backup_status_layout)
    auto_backup_status_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(auto_backup_status_wrapper, **SHADOW_EFFECT_ARGUMENTS))

    status_and_auto_backup_layout = QVBoxLayout()
    status_and_auto_backup_layout.addWidget(status_wrapper, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER, stretch=10)
    status_and_auto_backup_layout.addWidget(auto_backup_status_wrapper, alignment=ALIGNMENT.AlignTop, stretch=90)

    max_backups = QLineEdit()
    max_backups.setMinimumWidth(220)
    max_backups_validator = QRegularExpressionValidator(QRegularExpression(MAX_BACKUPS_VALIDATOR_REGEX))
    max_backups.setValidator(max_backups_validator)

    max_backups_label = QLabel("Max backups")
    max_backups_label.setMinimumSize(450, 150)
    max_backups_label.setWordWrap(True)
    max_backups_label.setFont(BASIC_FONT)
    max_backups_label.setProperty("class", "light-text")

    max_legacy_backups = QLineEdit()
    max_legacy_backups.setMinimumWidth(250)
    max_legacy_backups_validator = QRegularExpressionValidator(QRegularExpression(MAX_LEGACY_BACKUPS_VALIDATOR_REGEX))
    max_legacy_backups.setValidator(max_legacy_backups_validator)

    max_legacy_backups_label = QLabel("Max legacy backups")
    max_legacy_backups_label.setMinimumSize(450, 150)
    max_legacy_backups_label.setWordWrap(True)
    max_legacy_backups_label.setFont(BASIC_FONT)
    max_legacy_backups_label.setProperty("class", "light-text")

    no_auto_removal = QCheckBox("No auto removal")
    no_auto_removal.setFont(BASIC_FONT)
    no_auto_removal.setProperty("class", "light-text")

    max_backups_layout = QVBoxLayout()
    max_backups_layout.setContentsMargins(10, 0, 10, 10)
    max_backups_layout.addWidget(max_backups_label, alignment=ALIGN_H_CENTER)
    max_backups_layout.addWidget(max_backups, alignment=ALIGN_H_CENTER)
    max_backups_layout.addWidget(max_legacy_backups_label, alignment=ALIGN_H_CENTER)
    max_backups_layout.addWidget(max_legacy_backups, alignment=ALIGN_H_CENTER)
    max_backups_layout.addSpacing(30)
    max_backups_layout.addWidget(no_auto_removal, alignment=ALIGN_H_CENTER)

    max_backups_wrapper = QWidget()
    max_backups_wrapper.setProperty("class", "wrapper")
    max_backups_wrapper.setLayout(max_backups_layout)
    max_backups_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(max_backups_wrapper, **SHADOW_EFFECT_ARGUMENTS))

    status_and_max_backup_layout = QHBoxLayout()
    status_and_max_backup_layout.addLayout(status_and_auto_backup_layout)
    status_and_max_backup_layout.addWidget(max_backups_wrapper)

    save = create_button("Save", (100, 40))
    save.setFont(BASIC_FONT)
    save.setDefault(True)

    main_layout = QVBoxLayout()
    main_layout.addLayout(window.window_menu_layout)
    main_layout.setSpacing(25)
    main_layout.addLayout(status_and_max_backup_layout)
    main_layout.addWidget(save, alignment=ALIGN_H_CENTER)
    main_layout.setContentsMargins(20, 10, 20, 20)

    window.window_container.setLayout(main_layout)




