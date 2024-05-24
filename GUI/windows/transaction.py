from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QDialog
from PySide6.QtCore import Qt

from GUI.windows.main import APP_ICON, BASIC_FONT, ALIGMENT, close_dialog, create_button



class TransactionManagementWindow():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Edit")
    window.setWindowFlags(Qt.WindowType.Drawer & Qt.WindowType.Window)
    window.closeEvent = close_dialog

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
    main_layout.addStretch(1)
    main_layout.addWidget(message,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addLayout(transaction_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)

    window.setLayout(main_layout)