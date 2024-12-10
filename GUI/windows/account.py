from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QComboBox
from PySide6.QtGui import QIcon

from project_configuration import AVAILABLE_LANGUAGES, ROOT_DIRECTORY

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button

from GUI.gui_constants import ALIGMENT, BASIC_FONT
from GUI.windows.main_window import MainWindow



class AddAccountWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

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
    button.setDefault(True)

    current_balance = QLineEdit()
    current_balance.setPlaceholderText("Current balance")

    main_layout = QVBoxLayout()
    main_layout.setSpacing(20)
    main_layout.addLayout(window.window_menu_layout)
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
    main_layout.setContentsMargins(50, 10, 50, 30)

    window.window_container.setLayout(main_layout)



class RenameAccountWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)
    
    message = QLabel()
    message.setFont(BASIC_FONT)

    new_account_name = QLineEdit()
    account_name_layout = QHBoxLayout()
    account_name_layout.addWidget(new_account_name,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)

    button = create_button("Update", (160,40))
    button.setDefault(True)

    main_layout = QVBoxLayout()
    main_layout.setSpacing(20)
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(message,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addLayout(account_name_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.setContentsMargins(50, 10, 50, 30)

    window.window_container.setLayout(main_layout)