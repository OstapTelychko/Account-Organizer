from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QLabel
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from project_configuration import MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE, TRANSACTION_DAY_REGEX

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.strict_double_validator import StrictDoubleValidator
from DesktopQtToolkit.create_button import create_button

from GUI.gui_constants import ALIGN_H_CENTER, ALIGN_V_CENTER, BASIC_FONT

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow




class TransactionManagementWindow(SubWindow):
    """Represents Transaction management window structure.

        Warning
        -------
        This class contains non-GUI related objects like `transaction_id`\n
        `transaction_id` - is a variable that stores the ID of the transaction for editing or deleting.
    """
        
    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.message = QLabel()
        self.message.setFont(BASIC_FONT)

        self.transaction_layout = QHBoxLayout()
        self.transaction_name = QLineEdit()

        self.transaction_day = QLineEdit()
        self.day_regular_expression = QRegularExpression(TRANSACTION_DAY_REGEX)
        self.transaction_day_validator = QRegularExpressionValidator(self.day_regular_expression)
        self.transaction_day.setValidator(self.transaction_day_validator)

        self.transaction_value = QLineEdit()
        self.transaction_value_validator = StrictDoubleValidator(MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE, 2)
        self.transaction_value_validator.setNotation(StrictDoubleValidator.Notation.StandardNotation)
        self.transaction_value.setValidator(self.transaction_value_validator)

        self.transaction_id:int

        self.transaction_layout.addWidget(self.transaction_name, alignment=ALIGN_V_CENTER)
        self.transaction_layout.addWidget(self.transaction_day, alignment=ALIGN_V_CENTER)
        self.transaction_layout.addWidget(self.transaction_value, alignment=ALIGN_V_CENTER)

        self.button = create_button("", (150,40))
        self.button.setDefault(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(30)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.message, alignment=ALIGN_H_CENTER)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.transaction_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.button, alignment=ALIGN_H_CENTER)
        self.main_layout.addStretch(1)
        self.main_layout.setContentsMargins(30, 10, 30, 30)

        self.window_container.setLayout(self.main_layout)
        self.transaction_name.setFocus()