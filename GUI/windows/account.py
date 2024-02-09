from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QComboBox, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from GUI.windows.main import APP_ICON, BASIC_FONT, ALIGMENT, create_button, close_dialog
from project_configuration import AVAILABLE_LANGUAGES, ROOT_DIRECTORY



class AddAccountWindow():
    window = QDialog()
    window.resize(800,800)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Add account")
    window.setWindowFlags(Qt.WindowType.Drawer)
    window.closeEvent = close_dialog

    languages = QComboBox()
    languages.setFont(BASIC_FONT)
    languages.addItems(AVAILABLE_LANGUAGES)

    for language in range(len(AVAILABLE_LANGUAGES)):
        languages.setItemIcon(language, QIcon(f"{ROOT_DIRECTORY}/Images/{language}-flag.png"))

    languages_layout = QHBoxLayout()
    languages_layout.addWidget(languages, alignment=ALIGMENT.AlignRight)

    message = QLabel()
    message.setFont(BASIC_FONT)
    message.setWordWrap(True)
    message.setMinimumHeight(80)
    message.setMinimumWidth(450)

    account_name = QLineEdit()
    account_name.setPlaceholderText("Account Name")

    account_name_layout = QHBoxLayout()
    account_name_layout.addWidget(account_name, alignment=ALIGMENT.AlignCenter )

    button = create_button("", (140,50))
    current_balance = QLineEdit()
    current_balance.setPlaceholderText("Current balance")

    main_layout = QVBoxLayout()
    main_layout.addLayout(languages_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(message,alignment=ALIGMENT.AlignHCenter)    
    main_layout.addStretch(1)
    main_layout.addLayout(account_name_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(current_balance,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)

    window.setLayout(main_layout)



class RenameAccountWindow():
    window = QDialog()
    window.resize(800,800)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Rename account")
    window.setWindowFlags(Qt.WindowType.Drawer)
    window.closeEvent = close_dialog
    
    message = QLabel()
    message.setFont(BASIC_FONT)

    new_account_name = QLineEdit()
    account_name_layout = QHBoxLayout()
    account_name_layout.addWidget(new_account_name,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)

    button = create_button("Update", (160,40))

    main_layout = QVBoxLayout()
    main_layout.addStretch(1)
    main_layout.addWidget(message,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addLayout(account_name_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)

    window.setLayout(main_layout)