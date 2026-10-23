from __future__ import annotations
from typing import TYPE_CHECKING, NamedTuple
from datetime import date
from functools import partial
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.app_exceptions import ReminderValidationError
from DesktopQtToolkit.table_widget import CustomTableWidgetItem
from DesktopQtToolkit.Utils import get_table_widget_item
from GeneralTools.Utils import get_covered_period, get_due_date_for_covered_month
from GUI.gui_constants import ALIGNMENT
from GUI.windows.reminders import PendingReminderRow

from languages import LanguageStructure
from project_configuration import CategoryType, MIN_REMINDER_NAME_LENGTH, MIN_REMINDER_DAY, MAX_REMINDER_DAY,\
    DISPLAY_DATE_FORMAT
from AppManagement.date import set_month_and_year

if TYPE_CHECKING:
    from backend.models import MonthlyReminder



logger = get_logger(__name__)

REMINDERS_TABLE_ID_COLUMN = 5

class ReminderFormData(NamedTuple):
    """Data entered in the reminders management form."""

    name: str
    category_id: int | None
    value: float | None
    day: int | None


def get_covered_month_text(reminder:MonthlyReminder) -> str:
    """Get the covered month of a reminder formatted as `MM-YYYY` for logs.

        Arguments
        ---------
            `reminder` : (MonthlyReminder) - Reminder to format.
        Returns
        -------
            `str` - Covered month.
    """

    covered_start, _ = get_covered_period(reminder.next_due_date, reminder.day)
    return covered_start.strftime("%m-%Y")


def validate_reminder(name:str, category_id:int|None, day:int|None, exclude_reminder_id:int|None = None) -> int:
    """Validate reminder data. Raises `ReminderValidationError` with the reason if data is invalid.

        Arguments
        ---------
            `name` : (str) - Reminder name.
            `category_id` : (int|None) - Category ID. Mandatory.
            `day` : (int|None) - Day of the month. Optional.
            `exclude_reminder_id` : (int|None) - Reminder that is being updated (skipped in the name check).
        Returns
        -------
            `int` - Validated category ID.
    """

    if len(name.strip()) < MIN_REMINDER_NAME_LENGTH:
        raise ReminderValidationError(ReminderValidationError.NAME_TOO_SHORT)

    if category_id is None:
        raise ReminderValidationError(ReminderValidationError.NO_CATEGORY)

    if day is not None and not MIN_REMINDER_DAY <= day <= MAX_REMINDER_DAY:
        raise ReminderValidationError(ReminderValidationError.DAY_OUT_OF_RANGE)

    if AppCore.instance().db.reminder_query.reminder_name_exists(name, exclude_reminder_id):
        raise ReminderValidationError(ReminderValidationError.NAME_EXISTS)

    return category_id


def create_reminder(
        name:str,
        category_id:int|None,
        value:float|None,
        day:int|None,
        current_date:date|None = None
    ) -> MonthlyReminder:
    """Validate and create a reminder.

        Arguments
        ---------
            `name` : (str) - Reminder name.
            `category_id` : (int|None) - Category ID. Mandatory.
            `value` : (float|None) - Expected value.
            `day` : (int|None) - Day of the month.
            `current_date` : (date|None) - Date of creation. Defaults to `date.today()`.
        Returns
        -------
            `MonthlyReminder` - Created reminder.
    """

    name = name.strip()
    valid_category_id = validate_reminder(name, category_id, day)

    current_date = current_date or date.today()
    next_due_date = get_due_date_for_covered_month(current_date.year, current_date.month, day)
    return AppCore.instance().db.reminder_query.create_reminder(name, valid_category_id, value, day, next_due_date)


def is_reminder_paid(reminder:MonthlyReminder) -> bool:
    """Check if a transaction matching the reminder exists in its covered month.

        Arguments
        ---------
            `reminder` : (MonthlyReminder) - Reminder to check.
        Returns
        -------
            `bool` - True if the reminder is paid.
    """

    period_start, period_end = get_covered_period(reminder.next_due_date, reminder.day)
    return AppCore.instance().db.reminder_query.matching_transaction_exists(
        reminder.name, reminder.category_id, period_start, period_end
    )


def resolve_reminder(reminder:MonthlyReminder) -> date:
    """Move a paid reminder to the next month.

        Arguments
        ---------
            `reminder` : (MonthlyReminder) - Paid reminder. Its `next_due_date` is updated in place.
        Returns
        -------
            `date` - New next due date.
    """

    covered_month = get_covered_month_text(reminder)
    reminder.next_due_date = AppCore.instance().db.reminder_query.update_next_due_date(reminder.id)
    logger.info(
        f'[ENTITY: REMINDER] [ACTION: RESOLVED] name="{reminder.name}" month={covered_month} '
        f'next_due_date={reminder.next_due_date}'
    )
    return reminder.next_due_date


def check_pending_reminders(current_date:date|None = None) -> list[MonthlyReminder]:
    """Find due reminders without a matching transaction. Paid reminders are silently moved to the next month.

        Arguments
        ---------
            `current_date` : (date|None) - Date considered as today. Defaults to `date.today()`.
        Returns
        -------
            `list[MonthlyReminder]` - Unpaid due reminders of the current account.
    """

    current_date = current_date or date.today()
    pending:list[MonthlyReminder] = []

    for reminder in AppCore.instance().db.reminder_query.get_all_reminders():
        while current_date >= reminder.next_due_date:
            if not is_reminder_paid(reminder):
                pending.append(reminder)
                break
            resolve_reminder(reminder)

    return pending


def ignore_reminders(reminder_ids:list[int]) -> None:
    """Skip the covered month of the given reminders.

        Arguments
        ---------
            `reminder_ids` : (list[int]) - IDs of reminders to skip.
    """

    app_core = AppCore.instance()
    for reminder_id in reminder_ids:
        reminder = app_core.db.reminder_query.get_reminder(reminder_id)
        skipped_month = get_covered_month_text(reminder)
        app_core.db.reminder_query.update_next_due_date(reminder_id)
        logger.info(f'[ENTITY: REMINDER] [ACTION: IGNORED] name="{reminder.name}" skipped_for_month={skipped_month}')


def remove_pending_reminder_row(reminder_id:int) -> None:
    """Remove a reminder row from the pending reminders window. Other rows keep their state.

        Arguments
        ---------
            `reminder_id` : (int) - ID of the reminder whose row is removed.
    """

    row = WindowsRegistry.PendingRemindersWindow.reminder_rows.pop(reminder_id, None)
    if row is not None:
        row.setParent(None)
        row.deleteLater()


def clear_pending_reminder_rows() -> None:
    """Remove all rows from the pending reminders window."""

    for reminder_id in list(WindowsRegistry.PendingRemindersWindow.reminder_rows):
        remove_pending_reminder_row(reminder_id)


def show_pending_reminders(current_date:date|None = None) -> None:
    """Check reminders and show the pending reminders window if some of them are unpaid.

        Arguments
        ---------
            `current_date` : (date|None) - Date considered as today. Defaults to `date.today()`.
    """

    window = WindowsRegistry.PendingRemindersWindow
    if window.isVisible():
        return

    pending = check_pending_reminders(current_date)
    if len(pending) == 0:
        return

    clear_pending_reminder_rows()
    covered_months:set[tuple[int, int]] = set()
    for reminder in pending:
        covered_start, _ = get_covered_period(reminder.next_due_date, reminder.day)
        covered_months.add((covered_start.year, covered_start.month))

        row = PendingReminderRow()
        row.name_label.setText(reminder.name)
        row.category_label.setText(reminder.category.name)
        row.value_label.setText(
            str(reminder.value) if reminder.value is not None else LanguageStructure.GeneralManagement.get_translation(12)
        )
        row.pay_button.setText(LanguageStructure.Reminders.get_translation(2))
        row.ignore_checkbox.setText(LanguageStructure.Reminders.get_translation(3))
        row.pay_button.clicked.connect(partial(pay_reminder, reminder.id))
        row.double_clicked.connect(partial(pay_reminder, reminder.id))

        window.rows_layout.addWidget(row)
        window.reminder_rows[reminder.id] = row

    months_names = ", ".join(
        LanguageStructure.Months.get_translation(month) for _, month in sorted(covered_months)
    )
    window.description.setText(LanguageStructure.Reminders.get_translation(10).replace("%month%", months_names))

    logger.info(f"{len(pending)} pending reminders shown")
    window.exec()


def pay_reminder(reminder_id:int) -> None:
    """Open the add transaction window pre-filled with reminder data for its covered month.
    If the saved transaction matches the reminder, it is resolved and its row is removed.

        Arguments
        ---------
            `reminder_id` : (int) - ID of the reminder to pay.
    """

    app_core = AppCore.instance()
    reminder = app_core.db.reminder_query.get_reminder(reminder_id)
    covered_start, covered_end = get_covered_period(reminder.next_due_date, reminder.day)

    # The transaction window builds the date from the viewed month and year
    set_month_and_year(covered_start.month, covered_start.year)
    WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(
        CategoryType.get_index(reminder.category.category_type)
    )

    transaction_window = WindowsRegistry.TransactionManagementWindow
    transaction_window.button.setText(LanguageStructure.GeneralManagement.get_translation(1))
    transaction_window.message.setText(LanguageStructure.TransactionsMessages.get_translation(1))
    transaction_window.transaction_name.setText(reminder.name)
    transaction_window.transaction_day.setText(
        str(min(reminder.day, covered_end.day)) if reminder.day is not None else ""
    )
    transaction_window.transaction_value.setText(str(reminder.value) if reminder.value is not None else "")
    transaction_window.setWindowTitle(reminder.category.name)
    transaction_window.transaction_name.setFocus()
    transaction_window.exec()

    if not is_reminder_paid(reminder):
        return

    resolve_reminder(reminder)
    remove_pending_reminder_row(reminder_id)

    if len(WindowsRegistry.PendingRemindersWindow.reminder_rows) == 0:
        WindowsRegistry.PendingRemindersWindow.done(1)


def confirm_pending_reminders() -> None:
    """Skip reminders marked with \"Ignore this month\" and close the pending reminders window."""

    window = WindowsRegistry.PendingRemindersWindow
    ignored_ids = [
        reminder_id for reminder_id, row in window.reminder_rows.items() if row.ignore_checkbox.isChecked()
    ]
    ignore_reminders(ignored_ids)
    clear_pending_reminder_rows()
    window.done(1)


def load_reminders_table() -> None:
    """Load reminders of the current account into the management table."""

    table = WindowsRegistry.RemindersManagementWindow.reminders_table
    reminders = AppCore.instance().db.reminder_query.get_all_reminders()
    no_value = LanguageStructure.GeneralManagement.get_translation(12)

    table.setRowCount(0)
    table.setRowCount(len(reminders))

    for row, reminder in enumerate(reminders):
        cells = (
            reminder.name,
            reminder.category.name,
            str(reminder.value) if reminder.value is not None else no_value,
            str(reminder.day) if reminder.day is not None else no_value,
            reminder.next_due_date.strftime(DISPLAY_DATE_FORMAT),
            str(reminder.id)
        )
        for column, text in enumerate(cells):
            item = CustomTableWidgetItem(text)
            item.setFlags(~ Qt.ItemFlag.ItemIsEditable)
            item.setTextAlignment(ALIGNMENT.AlignCenter)
            table.setItem(row, column, item)


def clear_reminder_form() -> None:
    """Clear the reminder form fields."""

    window = WindowsRegistry.RemindersManagementWindow
    window.reminder_name.setText("")
    window.reminder_value.setText("")
    window.reminder_day.setText("")
    window.income_categories.clearSelection()
    window.expense_categories.clearSelection()


def show_reminders_management_window() -> None:
    """Show the monthly reminders management window."""

    window = WindowsRegistry.RemindersManagementWindow
    window.income_categories.clear()
    window.expense_categories.clear()
    for category in AppCore.instance().db.category_query.get_all_categories():
        item = QListWidgetItem(category.name)
        item.setData(Qt.ItemDataRole.UserRole, category.id)
        if category.category_type == CategoryType.Income:
            window.income_categories.addItem(item)
        else:
            window.expense_categories.addItem(item)

    load_reminders_table()
    clear_reminder_form()
    window.reminders_table.clearSelection()
    window.exec()


def get_selected_reminder_id() -> int|None:
    """Get the ID of the reminder selected in the management table.

        Returns
        -------
            `int|None` - Selected reminder ID or None if no row is selected.
    """

    table = WindowsRegistry.RemindersManagementWindow.reminders_table
    selected_rows = {item.row() for item in table.selectedItems()}
    if len(selected_rows) != 1:
        return None

    return int(get_table_widget_item(table, selected_rows.pop(), REMINDERS_TABLE_ID_COLUMN).text())


def fill_reminder_form_from_selection() -> None:
    """Fill the reminder form with data of the selected reminder."""

    reminder_id = get_selected_reminder_id()
    if reminder_id is None:
        return

    window = WindowsRegistry.RemindersManagementWindow
    reminder = AppCore.instance().db.reminder_query.get_reminder(reminder_id)
    window.reminder_name.setText(reminder.name)
    window.reminder_value.setText(str(reminder.value) if reminder.value is not None else "")
    window.reminder_day.setText(str(reminder.day) if reminder.day is not None else "")

    window.category_tabs.setCurrentIndex(CategoryType.get_index(reminder.category.category_type))
    categories_list = window.income_categories if reminder.category.category_type == CategoryType.Income\
        else window.expense_categories
    for row in range(categories_list.count()):
        if categories_list.item(row).data(Qt.ItemDataRole.UserRole) == reminder.category_id:
            categories_list.setCurrentRow(row)
            categories_list.scrollToItem(categories_list.item(row))


def read_reminder_form() -> ReminderFormData | None:
    """Read the reminder form. Shows a message and returns None if the value or day can't be parsed.

        Returns
        -------
            `ReminderFormData | None` - Entered reminder data.
    """

    window = WindowsRegistry.RemindersManagementWindow
    raw_value = window.reminder_value.text().strip().replace(",", ".")
    raw_day = window.reminder_day.text().strip()

    try:
        value = float(raw_value) if raw_value != "" else None
        day = int(raw_day) if raw_day != "" else None
    except ValueError:
        WindowsRegistry.Messages.incorrect_data_type.exec()
        return None

    # Only the category selected in the visible tab counts
    categories_list = window.income_categories if window.category_tabs.currentIndex() == 0 else window.expense_categories
    selected_items = categories_list.selectedItems()
    category_id = selected_items[0].data(Qt.ItemDataRole.UserRole) if selected_items else None
    return ReminderFormData(name=window.reminder_name.text(), category_id=category_id, value=value, day=day)


def show_reminder_validation_error(error:ReminderValidationError) -> int:
    """Show the message that matches the validation error reason.

        Arguments
        ---------
            `error` : (ReminderValidationError) - Validation error.
        Returns
        -------
            `int` - Result of the message window.
    """

    messages = {
        ReminderValidationError.NAME_TOO_SHORT: WindowsRegistry.Messages.reminder_name_too_short,
        ReminderValidationError.NAME_EXISTS: WindowsRegistry.Messages.reminder_already_exists,
        ReminderValidationError.NO_CATEGORY: WindowsRegistry.Messages.reminder_no_category,
        ReminderValidationError.DAY_OUT_OF_RANGE: WindowsRegistry.Messages.reminder_day_out_range,
    }
    return messages[error.reason].exec()


def add_reminder_from_form() -> int:
    """Create a reminder from the form data."""

    form_data = read_reminder_form()
    if form_data is None:
        return 0

    try:
        create_reminder(form_data.name, form_data.category_id, form_data.value, form_data.day)
    except ReminderValidationError as error:
        return show_reminder_validation_error(error)

    load_reminders_table()
    clear_reminder_form()
    return 1


def update_reminder_from_form() -> int:
    """Update the selected reminder with the form data.
    The covered month stays the same, so a day change only moves the due date inside it.
    """

    reminder_id = get_selected_reminder_id()
    if reminder_id is None:
        return WindowsRegistry.Messages.unselected_row.exec()

    form_data = read_reminder_form()
    if form_data is None:
        return 0

    name = form_data.name.strip()
    try:
        valid_category_id = validate_reminder(name, form_data.category_id, form_data.day, reminder_id)
    except ReminderValidationError as error:
        return show_reminder_validation_error(error)

    reminder_query = AppCore.instance().db.reminder_query
    reminder = reminder_query.get_reminder(reminder_id)
    covered_start, _ = get_covered_period(reminder.next_due_date, reminder.day)
    next_due_date = get_due_date_for_covered_month(covered_start.year, covered_start.month, form_data.day)
    reminder_query.update_reminder(
        reminder_id, name, valid_category_id, form_data.value, form_data.day, next_due_date
    )

    load_reminders_table()
    clear_reminder_form()
    return 1


def delete_selected_reminder() -> int:
    """Delete the selected reminder after confirmation."""

    reminder_id = get_selected_reminder_id()
    if reminder_id is None:
        return WindowsRegistry.Messages.unselected_row.exec()

    WindowsRegistry.Messages.delete_reminder_confirmation.exec()
    confirmation = WindowsRegistry.Messages.delete_reminder_confirmation
    if confirmation.clickedButton() != confirmation.ok_button:
        return 0

    AppCore.instance().db.reminder_query.delete_reminder(reminder_id)
    load_reminders_table()
    clear_reminder_form()
    return 1
