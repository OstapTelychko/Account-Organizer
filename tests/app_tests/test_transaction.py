from PySide6.QtCore import QTimer
from tests.tests_toolkit import DBTestCase, qsleep

from project_configuration import CATEGORY_TYPE
from AppObjects.session import Session

from GUI.windows.main_window import MainWindow
from GUI.windows.messages import Messages
from GUI.windows.transaction import TransactionManagementWindow


class TestTransaction(DBTestCase):
    """Test transaction management in the application."""


    def test_1_add_transaction(self):
        """Test adding transaction to the application."""

        for category in Session.categories.values():
            MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))

            def _add_transaction():
                """Set transaction data and click add button."""

                TransactionManagementWindow.transaction_name.setText("New test transaction")
                TransactionManagementWindow.transaction_day.setText("1")
                TransactionManagementWindow.transaction_value.setText("999")
                TransactionManagementWindow.button.click()

            QTimer.singleShot(100, _add_transaction)
            category.add_transaction.click()

        self.assertEqual(len(Session.db.transaction_query.get_all_transactions(self.income_category.id)), 2, "Income transaction hasn't been added")
        self.assertEqual(len(Session.db.transaction_query.get_all_transactions(self.expenses_category.id)), 2, "Expense transaction hasn't been added")
        self.assertEqual(Session.db.account_query.get_account().current_balance, 0, "Current balance has been changed after adding income and expense transactions with same value")

        qsleep(500)
    

    def test_2_update_transaction(self):
        """Test updating transaction in the application."""

        for category in Session.categories.values():
            MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))
            category.table_data.selectRow(0)

            def _update_transaction():
                """Set transaction data and click update button."""

                TransactionManagementWindow.transaction_name.setText("Updated transaction name")
                TransactionManagementWindow.transaction_day.setText("2")
                TransactionManagementWindow.transaction_value.setText("1000")
                TransactionManagementWindow.button.click()

            QTimer.singleShot(100, _update_transaction)
            category.edit_transaction.click()

        self.assertEqual(Session.db.transaction_query.get_all_transactions(self.income_category.id)[0].name, "Updated transaction name", "Income transaction hasn't been updated")
        self.assertEqual(Session.db.transaction_query.get_all_transactions(self.expenses_category.id)[0].name, "Updated transaction name", "Expense transaction hasn't been updated")
        self.assertEqual(Session.db.account_query.get_account().current_balance, 0, "Current balance has been changed after adding income and expense transactions with same value")

        qsleep(500)
    

    def test_3_delete_transaction(self):
        """Test deleting transaction from the application."""

        for category in Session.categories.values():
            self.select_correct_tab(category)
            category.table_data.selectRow(0)

            def _confirm_deletion():
                Messages.delete_transaction_confirmation.ok_button.click()

            QTimer.singleShot(100, _confirm_deletion)
            category.delete_transaction.click()

        self.assertEqual(len(Session.db.transaction_query.get_all_transactions(self.income_category.id)), 0, "Income transaction hasn't been deleted")
        self.assertEqual(len(Session.db.transaction_query.get_all_transactions(self.expenses_category.id)), 0, "Expense transaction hasn't been deleted")
        self.assertEqual(Session.db.account_query.get_account().current_balance, 0, "Current balance has been changed after adding income and expense transactions with same value")

        qsleep(500)
            
