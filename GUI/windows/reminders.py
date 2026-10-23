from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QLabel, QCheckBox, QHBoxLayout, QVBoxLayout, QScrollArea,\
    QLineEdit, QListWidget, QTabWidget, QHeaderView, QAbstractItemView
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import Qt, Signal, QRegularExpression

from project_configuration import MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE, TRANSACTION_DAY_REGEX

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.table_widget import CustomTableWidget
from DesktopQtToolkit.strict_double_validator import StrictDoubleValidator
from DesktopQtToolkit.create_wrapper_widget import create_wrapper_widget

from GUI.gui_constants import ALIGN_H_CENTER, ALIGN_V_CENTER, BASIC_FONT

if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent
    from GUI.windows.main_window import MainWindow



class PendingReminderRow(QWidget):
    """Represents a single unpaid reminder row. Emits `double_clicked` when the row is double-clicked."""

    double_clicked = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setProperty("class", "wrapper")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.name_label = QLabel()
        self.name_label.setFont(BASIC_FONT)
        self.name_label.setProperty("class", "light-text")

        self.category_label = QLabel()
        self.category_label.setFont(BASIC_FONT)
        self.category_label.setProperty("class", "light-text")

        self.value_label = QLabel()
        self.value_label.setFont(BASIC_FONT)
        self.value_label.setProperty("class", "light-text")

        self.pay_button = create_button("Pay", (110, 40))

        self.ignore_checkbox = QCheckBox("Ignore this month")
        self.ignore_checkbox.setFont(BASIC_FONT)
        self.ignore_checkbox.setProperty("class", "light-text")

        self.row_layout = QHBoxLayout()
        self.row_layout.setSpacing(20)
        self.row_layout.addWidget(self.name_label, 2, alignment=ALIGN_V_CENTER)
        self.row_layout.addWidget(self.category_label, 2, alignment=ALIGN_V_CENTER)
        self.row_layout.addWidget(self.value_label, 1, alignment=ALIGN_V_CENTER)
        self.row_layout.addWidget(self.pay_button, alignment=ALIGN_V_CENTER)
        self.row_layout.addWidget(self.ignore_checkbox, alignment=ALIGN_V_CENTER)
        self.setLayout(self.row_layout)


    def mouseDoubleClickEvent(self, event:QMouseEvent) -> None:
        """Emit `double_clicked` signal on double click."""

        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)



class PendingRemindersWindow(SubWindow):
    """Represents Pending reminders window structure.

        Warning
        -------
        This class contains non-GUI related objects like `reminder_rows`\n
        `reminder_rows` - maps reminder IDs to their rows.
    """

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.reminder_rows:dict[int, PendingReminderRow] = {}

        self.description = QLabel()
        self.description.setFont(BASIC_FONT)
        self.description.setWordWrap(True)
        self.description.setTextFormat(Qt.TextFormat.RichText)
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(15)
        self.rows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.rows_wrapper = QWidget()
        self.rows_wrapper.setLayout(self.rows_layout)

        self.rows_scroll_area = QScrollArea()
        self.rows_scroll_area.setWidgetResizable(True)
        self.rows_scroll_area.setStyleSheet("QScrollArea{border:none;background-color:transparent;}")
        self.rows_scroll_area.setWidget(self.rows_wrapper)
        self.rows_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.rows_scroll_area.setMinimumSize(850, 300)

        self.confirm_button = create_button("Confirm & Close", (240, 40))

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.addLayout(self.window_menu_layout)
        # No layout alignment flag: with it a word-wrapped label gets a too small height and is cropped
        self.main_layout.addWidget(self.description)
        self.main_layout.addWidget(self.rows_scroll_area)
        self.main_layout.addWidget(self.confirm_button, alignment=ALIGN_H_CENTER)
        self.main_layout.setContentsMargins(20, 10, 20, 20)

        self.window_container.setLayout(self.main_layout)



class RemindersManagementWindow(SubWindow):
    """Represents Monthly reminders management window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.reminders_table = CustomTableWidget()
        self.reminders_table.setProperty("class", "category_data")
        self.reminders_table.setColumnCount(6)
        self.reminders_table.setColumnHidden(5, True)
        self.reminders_table.setMinimumSize(750, 220)
        self.reminders_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.reminders_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        header = self.reminders_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)# Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)# Category
        header.setFont(BASIC_FONT)

        self.reminder_name = QLineEdit()
        self.reminder_name.setFont(BASIC_FONT)

        self.income_categories = QListWidget()
        self.expense_categories = QListWidget()
        for categories_list in (self.income_categories, self.expense_categories):
            categories_list.setFont(BASIC_FONT)
            categories_list.setWordWrap(True)
            categories_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            categories_list.setProperty("class", "category_data")

        # Tabs keep categories grouped by type, lists scroll and wrap long names
        self.category_tabs = QTabWidget()
        self.category_tabs.setFont(BASIC_FONT)
        self.category_tabs.addTab(self.income_categories, "Income")
        self.category_tabs.addTab(self.expense_categories, "Expenses")
        self.category_tabs.setFixedHeight(200)
        self.category_tabs.setMinimumWidth(350)
        # qdarktheme paints every QWidget dark, so the tab bar has to show the wrapper background
        self.category_tabs.setStyleSheet(
            "QTabWidget, QTabBar, QStackedWidget{background-color:transparent;} QTabWidget::pane{border:none;}"
        )

        self.reminder_value = QLineEdit()
        self.reminder_value.setFont(BASIC_FONT)
        self.reminder_value_validator = StrictDoubleValidator(MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE, 2)
        self.reminder_value_validator.setNotation(StrictDoubleValidator.Notation.StandardNotation)
        self.reminder_value.setValidator(self.reminder_value_validator)

        self.reminder_day = QLineEdit()
        self.reminder_day.setFont(BASIC_FONT)
        self.day_regular_expression = QRegularExpression(TRANSACTION_DAY_REGEX)
        self.reminder_day.setValidator(QRegularExpressionValidator(self.day_regular_expression))

        self.fields_layout = QVBoxLayout()
        self.fields_layout.setSpacing(15)
        self.fields_layout.addWidget(self.reminder_name)
        self.fields_layout.addWidget(self.reminder_value)
        self.fields_layout.addWidget(self.reminder_day)

        self.category_layout = QVBoxLayout()
        self.category_layout.addWidget(self.category_tabs)

        self.form_layout = QHBoxLayout()
        self.form_layout.setSpacing(25)
        self.form_layout.addWidget(create_wrapper_widget(self.fields_layout), 1)
        self.form_layout.addWidget(create_wrapper_widget(self.category_layout), 1)

        self.add_reminder = create_button("Add", (160, 40))
        self.update_reminder = create_button("Update", (160, 40))
        self.delete_reminder = create_button("Delete", (160, 40))

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.add_reminder, alignment=ALIGN_H_CENTER)
        self.buttons_layout.addWidget(self.update_reminder, alignment=ALIGN_H_CENTER)
        self.buttons_layout.addWidget(self.delete_reminder, alignment=ALIGN_H_CENTER)

        self.table_layout = QVBoxLayout()
        self.table_layout.addWidget(self.reminders_table)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(25)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(create_wrapper_widget(self.table_layout))
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.buttons_layout)
        self.main_layout.setContentsMargins(20, 10, 20, 20)

        self.window_container.setLayout(self.main_layout)
