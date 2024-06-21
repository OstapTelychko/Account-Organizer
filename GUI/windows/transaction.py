from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QLabel

from GUI.windows.main_window import BASIC_FONT, ALIGMENT, create_button, MainWindow
from CustomWidgets.sub_window import SubWindow



class TransactionManagementWindow():
    window = SubWindow()
    MainWindow.sub_windows.append(window)

    message = QLabel()
    message.setFont(BASIC_FONT)

    transaction_layout = QHBoxLayout()
    transaction_name = QLineEdit()
    transaction_day = QLineEdit()
    transaction_value = QLineEdit()
    transaction_id = None

    transaction_layout.addWidget(transaction_name,alignment=ALIGMENT.AlignVCenter)
    transaction_layout.addWidget(transaction_day,alignment=ALIGMENT.AlignVCenter)
    transaction_layout.addWidget(transaction_value,alignment=ALIGMENT.AlignVCenter)

    button = create_button("", (150,40))

    main_layout = QVBoxLayout()
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(message,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addLayout(transaction_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.setContentsMargins(30, 10, 30, 30)

    window.window_container.setLayout(main_layout)