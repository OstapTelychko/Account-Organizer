from PySide6.QtWidgets import QHeaderView, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QSizePolicy, QGraphicsDropShadowEffect

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.table_widget import CustomTableWidget

from GUI.windows.main_window import MainWindow
from GUI.gui_constants import BASIC_FONT, ALIGN_H_CENTER, SHADOW_EFFECT_ARGUMENTS



class DBManagementWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    backups_table = CustomTableWidget()
    backups_table.setColumnCount(2)
    backups_table.setMinimumSize(500, 300)
    backups_table.setProperty("class", "backups_table")

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
