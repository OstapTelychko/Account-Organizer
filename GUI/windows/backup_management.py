from PySide6.QtWidgets import QHeaderView, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QSizePolicy, QGraphicsDropShadowEffect, QCheckBox

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.table_widget import CustomTableWidget

from GUI.windows.main_window import MainWindow
from GUI.gui_constants import BASIC_FONT, ALIGN_H_CENTER, SHADOW_EFFECT_ARGUMENTS



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

    weekly = QCheckBox("Weekly")
    weekly.setFont(BASIC_FONT)

    daily = QCheckBox("Daily")
    daily.setFont(BASIC_FONT)

    save = create_button("Save", (100, 40))
    save.setFont(BASIC_FONT)

    buttons_layout = QVBoxLayout()
    buttons_layout.addWidget(monthly)
    buttons_layout.addWidget(weekly)
    buttons_layout.addWidget(daily)
    buttons_layout.addWidget(save, alignment=ALIGN_H_CENTER)

    buttons_wrapper = QWidget()
    buttons_wrapper.setProperty("class", "wrapper")
    buttons_wrapper.setLayout(buttons_layout)
    buttons_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(buttons_wrapper, **SHADOW_EFFECT_ARGUMENTS))

    main_layout = QVBoxLayout()
    main_layout.addLayout(window.window_menu_layout)
    main_layout.setSpacing(25)
    main_layout.addWidget(status_wrapper, alignment=ALIGN_H_CENTER)
    main_layout.addWidget(buttons_wrapper, alignment=ALIGN_H_CENTER)
    main_layout.setContentsMargins(20, 10, 20, 20)

    window.window_container.setLayout(main_layout)




