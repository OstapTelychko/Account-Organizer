from PySide6.QtWidgets import QWidget, QToolButton, QComboBox, QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtGui import QIcon

from project_configuration import AVAILABLE_LANGUAGES, APP_DIRECTORY

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button

from GUI.gui_constants import ALIGN_H_CENTER, ALIGN_V_CENTER, ICON_SIZE, SHADOW_EFFECT_ARGUMENTS, BASIC_FONT
from GUI.windows.main_window import MainWindow 



class SettingsWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)
    window.setStyleSheet("QComboBox:active,QComboBox:focus,QComboBox:disabled{border-color:transparent}")

    switch_themes_button = QToolButton()
    switch_themes_button.setIconSize(ICON_SIZE)

    languages = QComboBox()
    languages.setFont(BASIC_FONT)
    languages.addItems(AVAILABLE_LANGUAGES)

    for language in range(len(AVAILABLE_LANGUAGES)):
        languages.setItemIcon(language, QIcon(f"{APP_DIRECTORY}/Images/{language}-flag.png"))
    
    backup_management = create_button("Database management", (220, 50))

    gui_settings_wrapper_layout = QVBoxLayout()
    gui_settings_wrapper_layout.addWidget(switch_themes_button, alignment=ALIGN_H_CENTER)
    gui_settings_wrapper_layout.addWidget(languages, alignment=ALIGN_H_CENTER)
    gui_settings_wrapper_layout.addWidget(backup_management, alignment=ALIGN_H_CENTER)

    gui_settings_wrapper = QWidget()
    gui_settings_wrapper.setProperty("class", "wrapper")
    gui_settings_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(gui_settings_wrapper, **SHADOW_EFFECT_ARGUMENTS))
    gui_settings_wrapper.setLayout(gui_settings_wrapper_layout)
    gui_settings_wrapper.setMinimumHeight(220)
    gui_settings_wrapper.setMinimumWidth(250)


    accounts = QComboBox()
    accounts.setFont(BASIC_FONT)
    accounts.setMinimumWidth(250)
    accounts.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

    add_account = create_button("Add account",(180,50))

    rename_account = create_button("Rename account",(180,50))

    delete_account = create_button("Delete account",(180,50))
    delete_account.setStyleSheet("QPushButton{color:rgba(255,0,0,150); border-color:red;}")

    account_management_wrapper_layout = QVBoxLayout()
    account_management_wrapper_layout.addWidget(accounts, alignment=ALIGN_H_CENTER)
    account_management_wrapper_layout.addWidget(add_account, alignment=ALIGN_H_CENTER)
    account_management_wrapper_layout.addWidget(rename_account, alignment=ALIGN_H_CENTER)
    account_management_wrapper_layout.addWidget(delete_account, alignment=ALIGN_H_CENTER)

    account_management_wrapper = QWidget()
    account_management_wrapper.setLayout(account_management_wrapper_layout)
    account_management_wrapper.setProperty("class", "wrapper")
    account_management_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(account_management_wrapper, **SHADOW_EFFECT_ARGUMENTS))


    total_income = QLabel()
    total_income.setProperty("class", "light-text")
    total_income.setFont(BASIC_FONT)

    total_expense = QLabel()
    total_expense.setFont(BASIC_FONT)
    total_expense.setProperty("class", "light-text")

    account_created_date = QLabel()
    account_created_date.setFont(BASIC_FONT)
    account_created_date.setProperty("class", "light-text")

    app_version = QLabel()
    app_version.setFont(BASIC_FONT)
    app_version.setProperty("class", "light-text")

    account_info_wrapper_layout = QVBoxLayout()
    account_info_wrapper_layout.addWidget(total_income, alignment=ALIGN_H_CENTER)
    account_info_wrapper_layout.addWidget(total_expense, alignment=ALIGN_H_CENTER)
    account_info_wrapper_layout.addWidget(account_created_date, alignment=ALIGN_H_CENTER)
    account_info_wrapper_layout.addWidget(app_version, alignment=ALIGN_H_CENTER)

    account_info_wrapper = QWidget()
    account_info_wrapper.setProperty("class", "wrapper")
    account_info_wrapper.setLayout(account_info_wrapper_layout)
    account_info_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(account_info_wrapper, **SHADOW_EFFECT_ARGUMENTS))


    gui_settings_and_account_management = QHBoxLayout()
    gui_settings_and_account_management.addStretch(1)
    gui_settings_and_account_management.addWidget(gui_settings_wrapper, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
    gui_settings_and_account_management.addStretch(1)
    gui_settings_and_account_management.addWidget(account_management_wrapper, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
    gui_settings_and_account_management.addStretch(1)

    main_layout = QVBoxLayout()
    main_layout.setSpacing(20)
    main_layout.addStretch(1)
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addLayout(gui_settings_and_account_management)
    main_layout.addWidget(account_info_wrapper, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
    main_layout.addStretch(1)
    main_layout.setContentsMargins(50, 10, 50, 20)

    window.window_container.setLayout(main_layout)