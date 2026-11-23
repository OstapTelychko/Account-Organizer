from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import date, timedelta
import os
import shutil
import sqlite3
import tempfile

from alembic import command
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtTest import QTest

from tests.tests_toolkit import DBTestCase, OutOfScopeTestCase, qsleep
from languages import LanguageStructure
from project_configuration import CategoryType, InvestmentOperation, ReminderType, APP_DIRECTORY
from backend.models import Category, Transaction, MonthlyReminder
from backend.db_controller import create_alembic_config
from backend.investment_query import calculate_investment_timeline
from GeneralTools.Utils import shift_month, get_covered_period
from GUI.category import load_category
from GUI.gui_constants import INVESTMENTS_COLOR
from AppObjects.app_core import AppCore
from AppObjects.app_exceptions import ReminderValidationError
from AppObjects.windows_registry import WindowsRegistry
from AppManagement.balance import calculate_current_balance
from AppManagement.date import set_month_and_year
from AppManagement.category import update_category_total_value, reset_focused_category, remove_category
from AppManagement.transaction import show_add_transaction_window, show_edit_transaction_window, remove_transaction
from AppManagement.reminders_logic import (
    create_reminder, check_pending_reminders, pay_reminder, show_reminders_management_window
)
from AppManagement.shortcuts.shortcuts_actions import move_category_focus
from DesktopQtToolkit.Utils import get_table_widget_item
from Statistics.statistics import (
    get_net_result_text, show_monthly_statistics, show_quarterly_statistics, show_yearly_statistics,
    show_custom_range_statistics_view,
)

if TYPE_CHECKING:
    from typing import Callable
    from PySide6.QtWidgets import QListWidget
    from DesktopQtToolkit.sub_window import SubWindow


SECOND_ACCOUNT_NAME = "Investments second account"



class TestInvestments(DBTestCase, OutOfScopeTestCase):
    """Test Investments categories, their operations, reminders and statistics."""

    TIMEOUT_SEC = 15


    def setUp(self) -> None:
        """Create an Investments category in addition to the default income and expense ones."""

        app_core = AppCore.instance()
        self.today = date.today()
        app_core.db.category_query.create_category("Test investments category", CategoryType.Investment, 0)
        investment_category = app_core.db.category_query.get_category(
            "Test investments category", CategoryType.Investment
        )
        if investment_category is None:
            raise ValueError("Just created Investments category not found in the database")

        self.investment_category:Category = investment_category
        app_core.categories[investment_category.id] = load_category(
            investment_category, app_core.db, app_core.current_year, app_core.current_month
        )
        WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(
            CategoryType.get_index(CategoryType.Investment)
        )
        return super().setUp()


    def tearDown(self) -> None:
        set_month_and_year(self.today.month, self.today.year)
        super().tearDown()
        # Sync in-memory and stored balance with the cleaned database so other tests start from zero
        calculate_current_balance()


    def add_operation(self, operation_type:InvestmentOperation, value:float, operation_date:date|None = None) -> None:
        """Add an Investments operation directly to the database.

            Arguments
            ---------
                `operation_type` : (InvestmentOperation) - Type of the operation.
                `value` : (float) - Value of the operation.
                `operation_date` : (date|None) - Date of the operation. Defaults to today.
        """

        AppCore.instance().db.transaction_query.add_transaction(
            self.investment_category.id, operation_date or self.today, value, "", operation_type
        )


    def add_investment_category(self, name:str) -> Category:
        """Create an Investments category in the current account and load it into the application.

            Arguments
            ---------
                `name` : (str) - Name of the category.
            Returns
            -------
                `Category` - Created category.
        """

        app_core = AppCore.instance()
        app_core.db.category_query.create_category(name, CategoryType.Investment, 1)
        category = app_core.db.category_query.get_category(name, CategoryType.Investment)
        if category is None:
            raise ValueError("Just created Investments category not found in the database")
        app_core.categories[category.id] = load_category(
            category, app_core.db, app_core.current_year, app_core.current_month
        )
        return category


    def read_statistics(
            self,
            show_statistics:Callable[[], int],
            statistics_list:QListWidget,
            window:SubWindow
        ) -> str:
        """Show a statistics window, read the rows of one of its lists and close it.

            Arguments
            ---------
                `show_statistics` : (Callable[[], int]) - Function that shows the window.
                `statistics_list` : (QListWidget) - List to read.
                `window` : (SubWindow) - Shown window.
            Returns
            -------
                `str` - Joined rows of the list.
        """

        rows:list[str] = []

        def _read() -> None:
            self.assertTrue(window.isVisible(), "Statistics window hasn't been shown")
            rows.extend(statistics_list.item(index).text() for index in range(statistics_list.count()))
            window.done(1)

        QTimer.singleShot(100, self.catch_failure(_read))
        show_statistics()
        qsleep(300)
        return "".join(rows)


    def get_category_statistics_row(self, deposits:float, value:float) -> str:
        """Get the statistics row of the test Investments category without withdrawals and value changes.

            Arguments
            ---------
                `deposits` : (float) - Deposits of the period.
                `value` : (float) - Value at the end of the period.
            Returns
            -------
                `str` - Expected row.
        """

        return (
            LanguageStructure.Investments.get_translation(14)
            .replace("%category%", self.investment_category.name)
            .replace("%value%", f"<span style='color:{INVESTMENTS_COLOR}'>{value}</span>")
            .replace("%deposits%", f"<span style='color:red'>{deposits}</span>")
            .replace("%withdrawals%", "<span style='color:green'>0.0</span>")
            .replace("%change%", "<span style='color:green'>0.0</span>")
        )


    def find_operation_row(self, transaction_id:int) -> int:
        """Find the row of an operation in the table of the test Investments category.

            Arguments
            ---------
                `transaction_id` : (int) - ID of the operation.
            Returns
            -------
                `int` - Row of the operation.
        """

        table = AppCore.instance().categories[self.investment_category.id].table_data
        return next(
            row for row in range(table.rowCount())
            if get_table_widget_item(table, row, 3).text() == str(transaction_id)
        )


    def check_message_shown(self, message_name:str, show:Callable[[], object]) -> None:
        """Check that a message window is shown by the function and close it.

            Arguments
            ---------
                `message_name` : (str) - Name of the expected message window.
                `show` : (Callable[[], object]) - Function that should show the message.
        """

        message = getattr(WindowsRegistry.Messages, message_name)

        def _check_message() -> None:
            self.assertTrue(message.isVisible(), f"Message {message_name} wasn't shown")
            message.ok_button.click()

        QTimer.singleShot(100, self.catch_failure(_check_message))
        show()
        qsleep(300)


    def fill_transaction_window(self, operation_type:InvestmentOperation, day:int, value:float) -> None:
        """Fill Investments operation data in the transaction window and submit it.

            Arguments
            ---------
                `operation_type` : (InvestmentOperation) - Type of the operation.
                `day` : (int) - Day of the operation.
                `value` : (float) - Value of the operation.
        """

        window = WindowsRegistry.TransactionManagementWindow
        self.assertTrue(window.operation_type.isVisible(), "Operation type isn't shown for Investments category")
        window.operation_type.setCurrentIndex(window.operation_type.findData(int(operation_type)))
        window.transaction_day.setText(str(day))
        window.transaction_value.setText(str(value))
        self.click_on_widget(window.button)


    def check_rejected_operation(self, operation_type:InvestmentOperation, day:int, value:float, message_name:str) -> None:
        """Try to add an invalid Investments operation and check that the message is shown and nothing is saved.

            Arguments
            ---------
                `operation_type` : (InvestmentOperation) - Type of the operation.
                `day` : (int) - Day of the operation.
                `value` : (float) - Value of the operation.
                `message_name` : (str) - Name of the message window expected to be shown.
        """

        app_core = AppCore.instance()
        transactions_before = len(app_core.db.transaction_query.get_all_transactions(self.investment_category.id))
        message = getattr(WindowsRegistry.Messages, message_name)

        def _fill() -> None:
            def _check_message() -> None:
                self.assertTrue(message.isVisible(), f"Message {message_name} wasn't shown")
                message.ok_button.click()
                WindowsRegistry.TransactionManagementWindow.done(1)

            QTimer.singleShot(100, self.catch_failure(_check_message))
            self.fill_transaction_window(operation_type, day, value)

        QTimer.singleShot(100, self.catch_failure(_fill))
        show_add_transaction_window(self.investment_category.name)
        qsleep(300)

        self.assertEqual(
            len(app_core.db.transaction_query.get_all_transactions(self.investment_category.id)),
            transactions_before,
            f"Operation rejected with {message_name} has been saved"
        )


    def test_01_timeline(self) -> None:
        """Revaluation shows the market change, deposits on the same date are applied before revaluations."""

        timeline = calculate_investment_timeline([
            Transaction(id=3, date=date(2026, 10, 3), value=39000, operation_type=InvestmentOperation.Revaluation),
            Transaction(id=1, date=date(2026, 10, 1), value=32756, operation_type=InvestmentOperation.Deposit),
            Transaction(id=4, date=date(2026, 10, 3), value=1000, operation_type=InvestmentOperation.Deposit),
            Transaction(id=2, date=date(2026, 10, 2), value=4000, operation_type=InvestmentOperation.Deposit),
            Transaction(id=5, date=date(2026, 10, 4), value=500, operation_type=InvestmentOperation.Withdrawal),
        ])

        self.assertEqual([point.transaction_id for point in timeline], [1, 2, 4, 3, 5])
        self.assertEqual(timeline[3].value_after, 39000)
        self.assertEqual(timeline[3].value_change, 1244)
        self.assertEqual(timeline[-1].value_after, 38500)


    def test_02_balance(self) -> None:
        """Deposits lower the balance, revaluations change only the investments value, withdrawals return money."""

        app_core = AppCore.instance()

        self.add_operation(InvestmentOperation.Deposit, 4000, self.today - timedelta(days=2))
        calculate_current_balance()
        self.assertEqual(app_core.current_balance, -4000)
        self.assertEqual(app_core.investments_value, 4000)

        self.add_operation(InvestmentOperation.Revaluation, 4500, self.today - timedelta(days=1))
        calculate_current_balance()
        self.assertEqual(app_core.current_balance, -4000, "Revaluation has changed the balance")
        self.assertEqual(app_core.investments_value, 4500)

        self.add_operation(InvestmentOperation.Withdrawal, 1500)
        calculate_current_balance()
        self.assertEqual(app_core.current_balance, -2500)
        self.assertEqual(app_core.investments_value, 3000)
        self.assertIn(
            f" | {LanguageStructure.Investments.get_translation(0)}: 3000.0",
            WindowsRegistry.MainWindow.account_current_balance.text()
        )


    def test_03_add_operation_via_window(self) -> None:
        """Deposit added through the transaction window is saved with its operation type."""

        app_core = AppCore.instance()
        QTimer.singleShot(100, self.catch_failure(
            lambda: self.fill_transaction_window(InvestmentOperation.Deposit, self.today.day, 4000)
        ))
        show_add_transaction_window(self.investment_category.name)
        qsleep(300)

        transactions = app_core.db.transaction_query.get_all_transactions(self.investment_category.id)
        self.assertEqual(len(transactions), 1, "Deposit hasn't been added")
        self.assertEqual(transactions[0].operation_type, InvestmentOperation.Deposit)
        self.assertEqual(app_core.db.account_query.get_account().current_balance, -4000)
        self.assertEqual(app_core.categories[self.investment_category.id].table_data.rowCount(), 1)


    def test_04_rejected_operations(self) -> None:
        """Zero deposits, operations that make the value negative and future operations are rejected."""

        self.check_rejected_operation(InvestmentOperation.Deposit, self.today.day, 0, "zero_investment_value")
        self.check_rejected_operation(InvestmentOperation.Withdrawal, self.today.day, 100, "negative_investment_value")

        next_year, next_month = shift_month(self.today.year, self.today.month, 1)
        set_month_and_year(next_month, next_year)
        add_button = AppCore.instance().categories[self.investment_category.id].add_transaction
        self.assertFalse(add_button.isEnabled(), "Operations can be added to a future month")
        self.check_rejected_operation(InvestmentOperation.Deposit, 1, 100, "future_investment_operation")

        set_month_and_year(self.today.month, self.today.year)
        self.assertTrue(add_button.isEnabled(), "Operations can't be added to the current month")


    def test_05_remove_operation_check(self) -> None:
        """Deposit can't be removed if the following withdrawal would make the value negative."""

        app_core = AppCore.instance()
        self.add_operation(InvestmentOperation.Deposit, 1000)
        self.add_operation(InvestmentOperation.Withdrawal, 800)
        deposit_id = next(
            transaction.id for transaction in app_core.db.transaction_query.get_all_transactions(self.investment_category.id)
            if transaction.operation_type == InvestmentOperation.Deposit
        )
        update_category_total_value(self.investment_category.id)
        table = app_core.categories[self.investment_category.id].table_data
        table.selectRow(self.find_operation_row(deposit_id))

        def _check_message() -> None:
            self.assertTrue(WindowsRegistry.Messages.negative_investment_value.isVisible())
            WindowsRegistry.Messages.negative_investment_value.ok_button.click()

        QTimer.singleShot(100, self.catch_failure(_check_message))
        remove_transaction(table, self.investment_category.id)
        qsleep(300)

        self.assertEqual(
            len(app_core.db.transaction_query.get_all_transactions(self.investment_category.id)), 2,
            "Deposit has been removed"
        )


    def test_06_pay_reminder(self) -> None:
        """Paying an Investments transfer reminder opens a pre-filled deposit to an Investments category."""

        app_core = AppCore.instance()
        reminder = create_reminder(
            "Bonds", None, 4000, self.today.day, self.today - timedelta(days=40), ReminderType.InvestmentTransfer
        )
        window = WindowsRegistry.TransactionManagementWindow

        def _check_window() -> None:
            self.assertFalse(window.operation_type.isHidden(), "Operation type isn't shown for Investments reminder")
            self.assertEqual(window.operation_type.currentData(), InvestmentOperation.Deposit)
            self.assertEqual(window.windowTitle(), self.investment_category.name)
            self.assertEqual(window.transaction_value.text(), "4000.0")
            self.click_on_widget(window.button)

        QTimer.singleShot(100, self.catch_failure(_check_window))
        pay_reminder(reminder.id)
        qsleep(300)

        transactions = app_core.db.transaction_query.get_all_transactions(self.investment_category.id)
        self.assertEqual(
            [(transaction.operation_type, transaction.value) for transaction in transactions],
            [(InvestmentOperation.Deposit, 4000)]
        )
        self.assertGreater(
            app_core.db.reminder_query.get_reminder(reminder.id).next_due_date, reminder.next_due_date,
            "Paid reminder hasn't been moved to the next month"
        )


    def test_07_reminders(self) -> None:
        """Investments transfer reminder needs a deposit, revaluation reminder needs revaluation of every category."""

        transfer_reminder = create_reminder(
            "Bonds", None, 4000, 20, date(2026, 10, 15), ReminderType.InvestmentTransfer
        )
        self.assertIsNone(transfer_reminder.category_id)
        self.assertEqual([reminder.id for reminder in check_pending_reminders(date(2026, 10, 20))], [transfer_reminder.id])
        self.add_operation(InvestmentOperation.Deposit, 4000, date(2026, 9, 5))
        self.assertEqual(len(check_pending_reminders(date(2026, 10, 20))), 1, "Deposit of another month resolved reminder")
        self.add_operation(InvestmentOperation.Deposit, 4000, date(2026, 10, 5))
        self.assertEqual(check_pending_reminders(date(2026, 10, 20)), [])

        revaluation_reminder = create_reminder(
            "Revalue", None, None, 20, date(2026, 10, 15), ReminderType.InvestmentsRevaluation
        )
        self.assertEqual(
            [reminder.id for reminder in check_pending_reminders(date(2026, 10, 20))], [revaluation_reminder.id]
        )
        self.add_operation(InvestmentOperation.Revaluation, 8500, date(2026, 10, 10))
        self.assertEqual(check_pending_reminders(date(2026, 10, 20)), [])


    def test_08_monthly_statistics(self) -> None:
        """Monthly statistics show deposits and subtract them from the period result."""

        self.add_operation(InvestmentOperation.Deposit, 4000)
        calculate_current_balance()

        def _open_monthly_statistics() -> None:
            def _check_statistics() -> None:
                statistics_list = WindowsRegistry.MonthlyStatistics.statistics
                statistics = "".join(statistics_list.item(index).text() for index in range(statistics_list.count()))
                self.assertIn(
                    f"{LanguageStructure.Investments.get_translation(8)}<span style='color:red'>4000.0</span>",
                    statistics
                )
                self.assertIn(
                    LanguageStructure.Investments.get_translation(11)
                    + "<span style='color:red'>-4000.0</span> (<span style='color:red'>-400%</span>), "
                    + LanguageStructure.Investments.get_translation(15) + "0.0 (0%)",
                    statistics,
                )
                # Deposits aren't counted as expenses
                self.assertIn(f"{LanguageStructure.Statistics.get_translation(4)}1000.0", statistics)
                self.assertIn(f"{LanguageStructure.Statistics.get_translation(6)}1000.0", statistics)
                self.assertIn(self.get_category_statistics_row(4000.0, 4000.0), statistics)
                WindowsRegistry.MonthlyStatistics.done(1)

            QTimer.singleShot(100, self.catch_failure(_check_statistics))
            self.click_on_widget(WindowsRegistry.StatisticsWindow.monthly_statistics)

        QTimer.singleShot(100, self.catch_failure(_open_monthly_statistics))
        self.click_on_widget(WindowsRegistry.MainWindow.statistics)
        qsleep(500)


    def test_net_change_with_opening_investments(self) -> None:
        """Exclude prior holdings and count market changes, but not transfers, in the combined result."""
        self.add_operation(InvestmentOperation.Deposit, 500, date(2025, 12, 31))
        self.add_operation(InvestmentOperation.Deposit, 150, date(2026, 1, 2))
        self.add_operation(InvestmentOperation.Withdrawal, 25, date(2026, 1, 3))
        self.add_operation(InvestmentOperation.Revaluation, 645, date(2026, 1, 4))
        self.add_operation(InvestmentOperation.Revaluation, 600, date(2026, 2, 1))

        query = AppCore.instance().db.investment_query
        january = query.get_period_statistics([self.investment_category.id], date(2026, 1, 1), date(2026, 1, 31))
        february = query.get_period_statistics([self.investment_category.id], date(2026, 2, 1), date(2026, 2, 28))
        cash_label: str = LanguageStructure.Investments.get_translation(11)
        combined_label: str = LanguageStructure.Investments.get_translation(15)
        self.assertEqual(
            get_net_result_text(300.0, 100.0, january),
            f"{cash_label}75.0 (25%), {combined_label}220.0 (73.33%)",
        )
        self.assertEqual(
            get_net_result_text(0.0, 0.0, february),
            f"{cash_label}0.0 (—), {combined_label}<span style='color:red'>-45.0</span> (—)",
        )


    def test_09_focus_shortcuts(self) -> None:
        """Focus shortcuts move between Investments categories."""

        app_core = AppCore.instance()
        second_category = self.add_investment_category("Second investments category")
        reset_focused_category()

        move_category_focus(1)
        self.assertIs(app_core.focused_categories[CategoryType.Investment], app_core.categories[second_category.id])
        move_category_focus(-1)
        self.assertIs(
            app_core.focused_categories[CategoryType.Investment], app_core.categories[self.investment_category.id]
        )


    def test_10_revaluation_value_field(self) -> None:
        """Revaluation is pre-filled with the value at the entered day and accepts a typed 0."""

        app_core = AppCore.instance()
        previous_year, previous_month = shift_month(self.today.year, self.today.month, -1)
        self.add_operation(InvestmentOperation.Deposit, 1000, date(previous_year, previous_month, 1))
        self.add_operation(InvestmentOperation.Deposit, 500)
        window = WindowsRegistry.TransactionManagementWindow

        def _fill() -> None:
            window.transaction_value.clear()
            QTest.keyClicks(window.transaction_value, "0")
            self.assertEqual(window.transaction_value.text(), "", "Deposit accepts 0")
            QTest.keyClicks(window.transaction_value, "12,5")
            self.assertEqual(window.transaction_value.text(), "12.5", "Comma hasn't been converted to a dot")
            window.transaction_value.clear()

            window.operation_type.setCurrentIndex(window.operation_type.findData(int(InvestmentOperation.Revaluation)))
            self.assertEqual(window.transaction_value.text(), "1500.0")
            window.transaction_day.setText("1")
            self.assertEqual(window.transaction_value.text(), "1000.0" if self.today.day > 1 else "1500.0")

            window.transaction_value.clear()
            QTest.keyClicks(window.transaction_value, "0")
            self.assertEqual(window.transaction_value.text(), "0", "Revaluation doesn't accept 0")
            window.transaction_day.setText(str(self.today.day))
            self.assertEqual(window.transaction_value.text(), "0", "Value changed by the user has been replaced")
            self.click_on_widget(window.button)

        QTimer.singleShot(100, self.catch_failure(_fill))
        show_add_transaction_window(self.investment_category.name)
        qsleep(300)

        revaluations = [
            transaction for transaction in app_core.db.transaction_query.get_all_transactions(self.investment_category.id)
            if transaction.operation_type == InvestmentOperation.Revaluation
        ]
        self.assertEqual([transaction.value for transaction in revaluations], [0])
        calculate_current_balance()
        self.assertEqual(app_core.investments_value, 0)


    def test_11_delete_last_investment_category(self) -> None:
        """Deleting the last Investments category restores cash, hides the label and keeps its reminders waiting."""

        app_core = AppCore.instance()
        self.add_operation(InvestmentOperation.Deposit, 4000)
        calculate_current_balance()
        self.assertEqual(app_core.current_balance, -4000)
        reminder = create_reminder(
            "Bonds", None, 4000, self.today.day, self.today - timedelta(days=40), ReminderType.InvestmentTransfer
        )

        WindowsRegistry.CategorySettingsWindow.setWindowTitle(self.investment_category.name)
        QTimer.singleShot(100, self.catch_failure(
            lambda: WindowsRegistry.Messages.delete_category_confirmation.ok_button.click()
        ))
        remove_category()
        qsleep(300)

        self.assertEqual(app_core.current_balance, 0, "Deleted deposits are still subtracted from the balance")
        self.assertNotIn(
            f" | {LanguageStructure.Investments.get_translation(0)}",
            WindowsRegistry.MainWindow.account_current_balance.text()
        )
        self.assertEqual(check_pending_reminders(self.today), [])

        viewed_month = (app_core.current_year, app_core.current_month)
        self.check_message_shown("no_investment_categories", lambda: pay_reminder(reminder.id))
        self.assertEqual((app_core.current_year, app_core.current_month), viewed_month)
        self.assertEqual(
            app_core.db.reminder_query.get_reminder(reminder.id).next_due_date, reminder.next_due_date,
            "Reminder that can't be paid has been resolved"
        )


    def test_12_balance_label(self) -> None:
        """Label shows today's and projected balance and the investments value, later months show the last value."""

        app_core = AppCore.instance()
        self.add_operation(InvestmentOperation.Deposit, 4000)
        next_year, next_month = shift_month(self.today.year, self.today.month, 1)
        app_core.db.transaction_query.add_transaction(
            self.expenses_category.id, date(next_year, next_month, 1), 500, "Future expense"
        )
        calculate_current_balance()

        label_text = WindowsRegistry.MainWindow.account_current_balance.text()
        self.assertTrue(label_text.startswith(f"{LanguageStructure.MainWindow.get_translation(0)}-4000.0 (<a "))
        self.assertTrue(
            label_text.endswith(f">-4500.0</a>) | {LanguageStructure.Investments.get_translation(0)}: 4000.0"),
            label_text
        )

        set_month_and_year(next_month, next_year)
        category = app_core.categories[self.investment_category.id]
        self.assertEqual(category.total_value_label.text(), f"{LanguageStructure.Investments.get_translation(4)}4000.0")
        self.assertEqual(category.table_data.rowCount(), 0)


    def test_13_timeline_scenarios(self) -> None:
        """DCA after a revaluation, a forgotten earlier deposit and the value invariant."""

        operations = [
            Transaction(id=1, date=date(2026, 1, 5), value=1000, operation_type=InvestmentOperation.Deposit),
            Transaction(id=2, date=date(2026, 2, 5), value=1200, operation_type=InvestmentOperation.Revaluation),
            Transaction(id=3, date=date(2026, 3, 5), value=500, operation_type=InvestmentOperation.Deposit),
            Transaction(id=4, date=date(2026, 4, 5), value=1650, operation_type=InvestmentOperation.Revaluation),
            Transaction(id=5, date=date(2026, 5, 5), value=150, operation_type=InvestmentOperation.Withdrawal),
        ]
        timeline = calculate_investment_timeline(operations)
        self.assertEqual(timeline[2].value_after, 1700, "Deposit after a revaluation isn't added to the value")
        self.assertEqual(timeline[3].value_change, -50)

        deposits = sum(o.value for o in operations if o.operation_type == InvestmentOperation.Deposit)
        withdrawals = sum(o.value for o in operations if o.operation_type == InvestmentOperation.Withdrawal)
        changes = sum(
            point.value_change for point in timeline if point.operation_type == InvestmentOperation.Revaluation
        )
        self.assertEqual(timeline[-1].value_after, deposits - withdrawals + changes)

        forgotten_deposit = Transaction(
            id=6, date=date(2026, 1, 20), value=200, operation_type=InvestmentOperation.Deposit
        )
        timeline = calculate_investment_timeline([*operations, forgotten_deposit])
        revaluation = next(point for point in timeline if point.transaction_id == 2)
        self.assertEqual(revaluation.value_change, 0, "Earlier deposit hasn't been counted in the revaluation change")


    def test_14_several_assets_and_accounts(self) -> None:
        """Investments value sums every category of the current account only."""

        app_core = AppCore.instance()
        second_category = self.add_investment_category("Second investments category")
        self.add_operation(InvestmentOperation.Deposit, 1000)
        app_core.db.transaction_query.add_transaction(
            second_category.id, self.today, 2000, "", InvestmentOperation.Deposit
        )

        app_core.db.create_account(SECOND_ACCOUNT_NAME, 0)
        app_core.db.category_query.create_category("Other account investments", CategoryType.Investment, 0)
        other_category = app_core.db.category_query.get_category("Other account investments", CategoryType.Investment)
        if other_category is None:
            raise ValueError("Just created Investments category not found in the database")
        app_core.db.transaction_query.add_transaction(
            other_category.id, self.today, 5000, "", InvestmentOperation.Deposit
        )
        app_core.db.set_account_id("Test user")

        calculate_current_balance()
        self.assertEqual(app_core.investments_value, 3000)
        self.assertEqual(app_core.current_balance, -3000)


    def test_15_edit_earlier_deposit(self) -> None:
        """Editing an earlier deposit recalculates the change of the following revaluation."""

        app_core = AppCore.instance()
        self.add_operation(InvestmentOperation.Deposit, 1000, date(self.today.year, self.today.month, 1))
        self.add_operation(InvestmentOperation.Revaluation, 1500)
        transactions = app_core.db.transaction_query.get_all_transactions(self.investment_category.id)
        deposit_id = next(t.id for t in transactions if t.operation_type == InvestmentOperation.Deposit)
        revaluation_id = next(t.id for t in transactions if t.operation_type == InvestmentOperation.Revaluation)
        update_category_total_value(self.investment_category.id)
        table = app_core.categories[self.investment_category.id].table_data
        table.selectRow(self.find_operation_row(deposit_id))

        def _edit() -> None:
            window = WindowsRegistry.TransactionManagementWindow
            self.assertEqual(window.operation_type.currentData(), InvestmentOperation.Deposit)
            window.transaction_value.setText("1200")
            self.click_on_widget(window.button)

        QTimer.singleShot(100, self.catch_failure(_edit))
        show_edit_transaction_window(self.investment_category.name, table)
        qsleep(300)

        self.assertEqual(
            get_table_widget_item(table, self.find_operation_row(revaluation_id), 5).text(), "1500.0 (+300.0)"
        )
        self.assertEqual(app_core.current_balance, -1200)


    def test_16_period_statistics(self) -> None:
        """Quarterly, yearly and custom range statistics show the Investments block."""

        self.add_operation(InvestmentOperation.Deposit, 4000)
        investments_header = f"<br/><br/>{LanguageStructure.Investments.get_translation(0)}"
        category_row = self.get_category_statistics_row(4000.0, 4000.0)

        quarter = next(
            quarter for quarter in WindowsRegistry.QuarterlyStatistics.statistics.quarters
            if quarter.quarter_number == (self.today.month - 1) // 3 + 1
        )
        statistics = self.read_statistics(
            show_quarterly_statistics, quarter.total_quarter_statistics.data, WindowsRegistry.QuarterlyStatistics
        )
        self.assertIn(investments_header, statistics)
        self.assertIn(category_row, statistics)

        statistics = self.read_statistics(
            show_yearly_statistics,
            WindowsRegistry.YearlyStatistics.statistics.total_year_statistics.data,
            WindowsRegistry.YearlyStatistics
        )
        self.assertIn(investments_header, statistics)
        self.assertIn(category_row, statistics)

        custom_range = WindowsRegistry.CustomRangeStatistics
        custom_range.categories_selection.clear_categories_selection()
        from_date = self.today - timedelta(days=10)
        to_date = self.today + timedelta(days=1)
        custom_range.from_date.setDate(QDate(from_date.year, from_date.month, from_date.day))
        custom_range.to_date.setDate(QDate(to_date.year, to_date.month, to_date.day))
        statistics = self.read_statistics(
            show_custom_range_statistics_view,
            WindowsRegistry.CustomRangeStatisticsView.statistics_list,
            WindowsRegistry.CustomRangeStatisticsView
        )
        self.assertIn(investments_header, statistics)
        self.assertIn(category_row, statistics)


    def test_17_statistics_of_single_type(self) -> None:
        """Statistics are shown for Investments operations only and skip empty income and expense blocks."""

        app_core = AppCore.instance()

        def _show_statistics_without_categories() -> None:
            categories = app_core.categories
            app_core.categories = {}
            try:
                show_monthly_statistics()
            finally:
                app_core.categories = categories

        self.check_message_shown("no_category", _show_statistics_without_categories)

        app_core.db.transaction_query.delete_transaction(self.income_transaction.id)
        app_core.db.transaction_query.delete_transaction(self.expenses_transaction.id)
        self.check_message_shown("no_transactions", show_monthly_statistics)

        self.add_operation(InvestmentOperation.Deposit, 4000)
        statistics = self.read_statistics(
            show_monthly_statistics, WindowsRegistry.MonthlyStatistics.statistics, WindowsRegistry.MonthlyStatistics
        )
        self.assertIn(f"<br/><br/>{LanguageStructure.Investments.get_translation(0)}", statistics)
        self.assertNotIn(f"<br/><br/>{LanguageStructure.MainWindow.get_translation(1)}", statistics)
        self.assertNotIn(f"<br/><br/>{LanguageStructure.MainWindow.get_translation(2)}", statistics)


    def test_18_revaluation_reminder_skips_empty_category(self) -> None:
        """Revaluation reminder doesn't wait for categories whose value is zero."""

        empty_category = self.add_investment_category("Sold investments category")
        app_core = AppCore.instance()
        app_core.db.transaction_query.add_transaction(
            empty_category.id, date(2026, 9, 1), 1000, "", InvestmentOperation.Deposit
        )
        app_core.db.transaction_query.add_transaction(
            empty_category.id, date(2026, 9, 2), 1000, "", InvestmentOperation.Withdrawal
        )
        self.add_operation(InvestmentOperation.Deposit, 1000, date(2026, 9, 1))
        reminder = create_reminder("Revalue", None, None, 20, date(2026, 10, 15), ReminderType.InvestmentsRevaluation)
        self.assertEqual([pending.id for pending in check_pending_reminders(date(2026, 10, 20))], [reminder.id])
        self.add_operation(InvestmentOperation.Revaluation, 1100, date(2026, 10, 10))
        self.assertEqual(check_pending_reminders(date(2026, 10, 20)), [], "Category with zero value hasn't been skipped")


    def test_19_pay_revaluation_reminder(self) -> None:
        """Paying a revaluation reminder opens a revaluation pre-filled with the category value."""

        app_core = AppCore.instance()
        reminder = create_reminder(
            "Revalue", None, None, self.today.day, self.today - timedelta(days=40), ReminderType.InvestmentsRevaluation
        )
        covered_start, _ = get_covered_period(reminder.next_due_date, reminder.day)
        self.add_operation(InvestmentOperation.Deposit, 1000, covered_start)
        window = WindowsRegistry.TransactionManagementWindow

        def _check_window() -> None:
            self.assertEqual(window.windowTitle(), self.investment_category.name)
            self.assertEqual(window.operation_type.currentData(), InvestmentOperation.Revaluation)
            self.assertEqual(window.transaction_value.text(), "1000.0")
            window.transaction_value.setText("1100")
            self.click_on_widget(window.button)

        QTimer.singleShot(100, self.catch_failure(_check_window))
        pay_reminder(reminder.id)
        qsleep(300)

        self.assertGreater(
            app_core.db.reminder_query.get_reminder(reminder.id).next_due_date, reminder.next_due_date,
            "Paid revaluation reminder hasn't been moved to the next month"
        )


    def test_20_reminder_validation_and_form(self) -> None:
        """Regular reminder can't use an Investments category, revaluation reminder has no value field."""

        with self.assertRaises(ReminderValidationError) as error:
            create_reminder("Investments bill", self.investment_category.id, 100, 5)
        self.assertEqual(error.exception.reason, ReminderValidationError.INVESTMENT_CATEGORY)

        window = WindowsRegistry.RemindersManagementWindow

        def _check_value_field() -> None:
            window.category_tabs.setCurrentIndex(CategoryType.get_index(CategoryType.Investment))
            for row in range(window.investment_reminder_types.count()):
                window.investment_reminder_types.setCurrentRow(row)
                reminder_type = window.investment_reminder_types.item(row).data(Qt.ItemDataRole.UserRole)
                self.assertEqual(
                    window.reminder_value.isHidden(), reminder_type == ReminderType.InvestmentsRevaluation,
                    f"Wrong value field visibility for reminder type {reminder_type}"
                )
            window.category_tabs.setCurrentIndex(CategoryType.get_index(CategoryType.Income))
            self.assertFalse(window.reminder_value.isHidden())
            window.done(1)

        QTimer.singleShot(100, self.catch_failure(_check_value_field))
        show_reminders_management_window()
        qsleep(300)


    def test_21_account_deletion_removes_investments_reminders(self) -> None:
        """Deleting an account removes its Investments reminders."""

        app_core = AppCore.instance()
        create_reminder("Bonds", None, 4000, 5, reminder_type=ReminderType.InvestmentTransfer)
        app_core.db.create_account(SECOND_ACCOUNT_NAME, 0)
        create_reminder("Second account bonds", None, 100, 5, reminder_type=ReminderType.InvestmentTransfer)
        create_reminder("Second account revaluation", None, None, 5, reminder_type=ReminderType.InvestmentsRevaluation)
        app_core.db.account_query.delete_account()
        app_core.db.set_account_id("Test user")

        with app_core.db.session_factory() as session:
            remaining_names = [reminder.name for reminder in session.query(MonthlyReminder).all()]
        self.assertEqual(remaining_names, ["Bonds"], "Investments reminders of the deleted account haven't been removed")


    def test_22_migration(self) -> None:
        """Investments migration keeps existing data and its downgrade removes Investments reminders."""

        temp_directory = tempfile.mkdtemp()
        db_path = os.path.join(temp_directory, "migration.sqlite")
        alembic_config = create_alembic_config(APP_DIRECTORY, f"sqlite:///{db_path}")
        try:
            command.upgrade(alembic_config, "c3d4e5f6a7b8")
            with sqlite3.connect(db_path) as connection:
                connection.execute(
                    "INSERT INTO accounts (id, name, current_balance, current_total_income, current_total_expenses, "
                    "start_balance, created_date) VALUES (7, 'Migrated', 0, 0, 0, 0, '2026-01-01 00:00:00')"
                )
                connection.execute(
                    "INSERT INTO categories (id, name, category_type, position, account_id) "
                    "VALUES (3, 'Food', 'Expenses', 0, 7)"
                )
                connection.execute(
                    "INSERT INTO transactions (date, value, name, category_id) VALUES ('2026-01-05', 10, 'Bread', 3)"
                )
                connection.execute(
                    "INSERT INTO monthly_reminders (name, value, day, next_due_date, category_id) "
                    "VALUES ('Groceries', 100, 5, '2026-02-05', 3)"
                )
            connection.close()

            command.upgrade(alembic_config, "d4e5f6a7b8c9")
            with sqlite3.connect(db_path) as connection:
                self.assertEqual(connection.execute("SELECT operation_type FROM transactions").fetchall(), [(0,)])
                self.assertEqual(
                    connection.execute("SELECT account_id, reminder_type FROM monthly_reminders").fetchall(), [(7, 0)]
                )
                connection.execute(
                    "INSERT INTO monthly_reminders (name, value, day, next_due_date, category_id, account_id, "
                    "reminder_type) VALUES ('Bonds', 100, 5, '2026-02-05', NULL, 7, 1)"
                )
            connection.close()

            command.downgrade(alembic_config, "c3d4e5f6a7b8")
            with sqlite3.connect(db_path) as connection:
                transactions_columns = [row[1] for row in connection.execute("PRAGMA table_info(transactions)")]
                reminders_columns = [row[1] for row in connection.execute("PRAGMA table_info(monthly_reminders)")]
                reminder_names = connection.execute("SELECT name FROM monthly_reminders").fetchall()
            connection.close()
            self.assertNotIn("operation_type", transactions_columns)
            self.assertNotIn("account_id", reminders_columns)
            self.assertNotIn("reminder_type", reminders_columns)
            self.assertEqual(reminder_names, [("Groceries",)])
        finally:
            shutil.rmtree(temp_directory, ignore_errors=True)


    def test_23_rejected_edit(self) -> None:
        """Editing a deposit so that a later withdrawal makes the value negative is rejected and nothing changes."""

        app_core = AppCore.instance()
        self.add_operation(InvestmentOperation.Deposit, 1000, date(self.today.year, self.today.month, 1))
        self.add_operation(InvestmentOperation.Withdrawal, 800)
        deposit_id = next(
            transaction.id for transaction in app_core.db.transaction_query.get_all_transactions(self.investment_category.id)
            if transaction.operation_type == InvestmentOperation.Deposit
        )
        update_category_total_value(self.investment_category.id)
        table = app_core.categories[self.investment_category.id].table_data
        table.selectRow(self.find_operation_row(deposit_id))
        message = WindowsRegistry.Messages.negative_investment_value

        def _edit() -> None:
            def _check_message() -> None:
                self.assertTrue(message.isVisible(), "Message negative_investment_value wasn't shown")
                message.ok_button.click()
                WindowsRegistry.TransactionManagementWindow.done(1)

            QTimer.singleShot(100, self.catch_failure(_check_message))
            WindowsRegistry.TransactionManagementWindow.transaction_value.setText("500")
            self.click_on_widget(WindowsRegistry.TransactionManagementWindow.button)

        QTimer.singleShot(100, self.catch_failure(_edit))
        show_edit_transaction_window(self.investment_category.name, table)
        qsleep(300)

        deposit = next(
            transaction for transaction in app_core.db.transaction_query.get_all_transactions(self.investment_category.id)
            if transaction.id == deposit_id
        )
        self.assertEqual(deposit.value, 1000, "Rejected edit of the deposit has been saved")
