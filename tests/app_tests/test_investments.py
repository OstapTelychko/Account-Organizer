from __future__ import annotations
from datetime import date, timedelta

from PySide6.QtCore import QTimer

from tests.tests_toolkit import DBTestCase, OutOfScopeTestCase, qsleep
from languages import LanguageStructure
from project_configuration import CategoryType, InvestmentOperation, ReminderType
from backend.models import Category, Transaction
from backend.investment_query import calculate_investment_timeline
from GeneralTools.Utils import shift_month
from GUI.category import load_category
from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry
from AppManagement.balance import calculate_current_balance
from AppManagement.date import set_month_and_year
from AppManagement.category import update_category_total_value
from AppManagement.transaction import show_add_transaction_window, remove_transaction
from AppManagement.reminders_logic import create_reminder, check_pending_reminders
from DesktopQtToolkit.Utils import get_table_widget_item



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
            f"{LanguageStructure.Investments.get_translation(1)}3000.0",
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
        self.check_rejected_operation(InvestmentOperation.Deposit, 1, 100, "future_investment_operation")


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
        deposit_row = next(
            row for row in range(table.rowCount()) if get_table_widget_item(table, row, 3).text() == str(deposit_id)
        )
        table.selectRow(deposit_row)

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


    def test_06_monthly_investments_window(self) -> None:
        """Monthly investments window saves deposits and new values of categories."""

        app_core = AppCore.instance()
        window = WindowsRegistry.MonthlyInvestmentsWindow

        def _fill() -> None:
            self.assertEqual(window.investments_table.rowCount(), 1)
            window.total_amount.setText("5000")
            get_table_widget_item(window.investments_table, 0, 2).setText("4000")
            self.assertIn("1000.0", window.remaining_amount.text())
            get_table_widget_item(window.investments_table, 0, 3).setText("4100")
            self.click_on_widget(window.save_button)

        QTimer.singleShot(100, self.catch_failure(_fill))
        self.click_on_widget(WindowsRegistry.MainWindow.monthly_investments)
        qsleep(300)

        operations = {
            transaction.operation_type: transaction.value
            for transaction in app_core.db.transaction_query.get_all_transactions(self.investment_category.id)
        }
        self.assertEqual(operations, {InvestmentOperation.Deposit: 4000, InvestmentOperation.Revaluation: 4100})
        self.assertEqual(app_core.current_balance, -4000)
        self.assertEqual(app_core.investments_value, 4100)


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
                self.assertIn(f"{LanguageStructure.Investments.get_translation(9)}4000.0", statistics)
                self.assertIn(f"{LanguageStructure.Investments.get_translation(12)}-4000.0", statistics)
                WindowsRegistry.MonthlyStatistics.done(1)

            QTimer.singleShot(100, self.catch_failure(_check_statistics))
            self.click_on_widget(WindowsRegistry.StatisticsWindow.monthly_statistics)

        QTimer.singleShot(100, self.catch_failure(_open_monthly_statistics))
        self.click_on_widget(WindowsRegistry.MainWindow.statistics)
        qsleep(500)
