from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QLabel
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from project_configuration import MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.strict_double_validator import StrictDoubleValidator
from DesktopQtToolkit.create_button import create_button

from GUI.gui_constants import ALIGN_H_CENTER, ALIGN_V_CENTER, BASIC_FONT
from GUI.windows.main_window import MainWindow

from project_configuration import TRANSACTION_DAY_REGEX



class TransactionManagementWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    message = QLabel()
    message.setFont(BASIC_FONT)

    transaction_layout = QHBoxLayout()
    transaction_name = QLineEdit()

    transaction_day = QLineEdit()
    day_regularexpression = QRegularExpression(TRANSACTION_DAY_REGEX)
    transaction_day_validator = QRegularExpressionValidator(day_regularexpression)
    transaction_day.setValidator(transaction_day_validator)

    transaction_value = QLineEdit()
    transaction_value_validator = StrictDoubleValidator(MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE, 2)
    transaction_value_validator.setNotation(StrictDoubleValidator.Notation.StandardNotation)
    transaction_value.setValidator(transaction_value_validator)

    transaction_id = None

    transaction_layout.addWidget(transaction_name, alignment=ALIGN_V_CENTER)
    transaction_layout.addWidget(transaction_day, alignment=ALIGN_V_CENTER)
    transaction_layout.addWidget(transaction_value, alignment=ALIGN_V_CENTER)

    button = create_button("", (150,40))
    button.setDefault(True)

    main_layout = QVBoxLayout()
    main_layout.setSpacing(30)
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(message, alignment=ALIGN_H_CENTER)
    main_layout.addStretch(1)
    main_layout.addLayout(transaction_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(button, alignment=ALIGN_H_CENTER)
    main_layout.addStretch(1)
    main_layout.setContentsMargins(30, 10, 30, 30)

    window.window_container.setLayout(main_layout)