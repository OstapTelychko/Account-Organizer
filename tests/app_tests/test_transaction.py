from PySide6.QtCore import QTimer
from tests.tests_toolkit import DBTestCase, OutOfScopeTestCase, qsleep

from project_configuration import CATEGORY_TYPE
from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry



class TestTransaction(DBTestCase, OutOfScopeTestCase):
    """Test transaction management in the application."""


    def test_1_add_transaction(self) -> None:
        """Test adding transaction to the application."""

        app_core = AppCore.instance()
        for category in app_core.categories.values():
            WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))

            def _add_transaction() -> None:
                """Set transaction data and click add button."""

                WindowsRegistry.TransactionManagementWindow.transaction_name.setText("New test transaction")
                WindowsRegistry.TransactionManagementWindow.transaction_day.setText("1")
                WindowsRegistry.TransactionManagementWindow.transaction_value.setText("999")
                WindowsRegistry.TransactionManagementWindow.button.click()

            QTimer.singleShot(100, self.catch_failure(_add_transaction))
            category.add_transaction.click()

        self.assertEqual(
            len(app_core.db.transaction_query.get_all_transactions(self.income_category.id)),
            2,
            "Income transaction hasn't been added"
        )
        self.assertEqual(
            len(app_core.db.transaction_query.get_all_transactions(self.expenses_category.id)),
            2,
            "Expense transaction hasn't been added"
        )
        self.assertEqual(
            app_core.db.account_query.get_account().current_balance,
            0,
            "Current balance has been changed after adding income and expense transactions with same value"
        )

        qsleep(500)
    

    def test_2_update_transaction(self) -> None:
        """Test updating transaction in the application."""

        app_core = AppCore.instance()
        for category in app_core.categories.values():
            WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))
            category.table_data.selectRow(0)

            def _update_transaction() -> None:
                """Set transaction data and click update button."""

                WindowsRegistry.TransactionManagementWindow.transaction_name.setText("Updated transaction name")
                WindowsRegistry.TransactionManagementWindow.transaction_day.setText("2")
                WindowsRegistry.TransactionManagementWindow.transaction_value.setText("1000")
                WindowsRegistry.TransactionManagementWindow.button.click()

            QTimer.singleShot(100, self.catch_failure(_update_transaction))
            category.edit_transaction.click()

        self.assertEqual(
            app_core.db.transaction_query.get_all_transactions(self.income_category.id)[0].name,
            "Updated transaction name",
            "Income transaction hasn't been updated"
        )
        self.assertEqual(
            app_core.db.transaction_query.get_all_transactions(self.expenses_category.id)[0].name,
            "Updated transaction name",
            "Expense transaction hasn't been updated"
        )
        self.assertEqual(
            app_core.db.account_query.get_account().current_balance,
            0,
            "Current balance has been changed after adding income and expense transactions with same value"
        )

        qsleep(500)
    

    def test_3_delete_transaction(self) -> None:
        """Test deleting transaction from the application."""

        app_core = AppCore.instance()
        for category in app_core.categories.values():
            self.select_correct_tab(category)
            category.table_data.selectRow(0)

            def _confirm_deletion() -> None:
                WindowsRegistry.Messages.delete_transaction_confirmation.ok_button.click()

            QTimer.singleShot(100, self.catch_failure(_confirm_deletion))
            category.delete_transaction.click()

        self.assertEqual(
            len(app_core.db.transaction_query.get_all_transactions(self.income_category.id)),
            0,
            "Income transaction hasn't been deleted"
        )
        self.assertEqual(
            len(app_core.db.transaction_query.get_all_transactions(self.expenses_category.id)),
            0,
            "Expense transaction hasn't been deleted"
        )
        self.assertEqual(
            app_core.db.account_query.get_account().current_balance,
            0,
            "Current balance has been changed after adding income and expense transactions with same value"
        )

        qsleep(500)
            
