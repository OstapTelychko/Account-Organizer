from PySide6.QtCore import QTimer, QEventLoop
from tests.tests_toolkit import DBTestCase, OK_BUTTON

from project_configuration import CATEGORY_TYPE
from AppObjects.session import Session

from GUI.windows.main_window import MainWindow
from GUI.windows.messages import Messages
from GUI.windows.transaction import TransactionManagementWindow


class TestTransaction(DBTestCase):

    def test_add_transaction(self):
        for category in Session.categories.values():
            MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))

            def add_transaction():
                TransactionManagementWindow.transaction_name.setText("New test transaction")
                TransactionManagementWindow.transaction_day.setText("1")
                TransactionManagementWindow.transaction_value.setText("999")
                TransactionManagementWindow.button.click()

            QTimer.singleShot(100, add_transaction)
            category.add_transaction.click()

        self.assertEqual(len(Session.db.get_all_transactions(self.income_category.id)), 2, "Income transaction hasn't been added")
        self.assertEqual(len(Session.db.get_all_transactions(self.expenses_category.id)), 2, "Expense transaction hasn't been added")
        self.assertEqual(Session.db.get_account().current_balance, 0, "Current balance has been changed after adding income and expense transactions with same value")

        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec()
    

    def test_update_transaction(self):
        for category in Session.categories.values():
            MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))
            category.table_data.selectRow(0)

            def update_transaction():
                TransactionManagementWindow.transaction_name.setText("Updated transaction name")
                TransactionManagementWindow.transaction_day.setText("2")
                TransactionManagementWindow.transaction_value.setText("1000")
                TransactionManagementWindow.button.click()

            QTimer.singleShot(100, update_transaction)
            category.edit_transaction.click()

        self.assertEqual(Session.db.get_all_transactions(self.income_category.id)[0].name, "Updated transaction name", "Income transaction hasn't been updated")
        self.assertEqual(Session.db.get_all_transactions(self.expenses_category.id)[0].name, "Updated transaction name", "Expense transaction hasn't been updated")
        self.assertEqual(Session.db.get_account().current_balance, 0, "Current balance has been changed after adding income and expense transactions with same value")

        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec()
    

    def test_delete_transaction(self):
        for category in Session.categories.values():
            self.select_correct_tab(category)
            category.table_data.selectRow(0)

            def confirm_deletion():
                Messages.delete_transaction_confirmation.button(OK_BUTTON).click()

            QTimer.singleShot(100, confirm_deletion)
            category.delete_transaction.click()

        self.assertEqual(len(Session.db.get_all_transactions(self.income_category.id)), 0, "Income transaction hasn't been deleted")
        self.assertEqual(len(Session.db.get_all_transactions(self.expenses_category.id)), 0, "Expense transaction hasn't been deleted")
        self.assertEqual(Session.db.get_account().current_balance, 0, "Current balance has been changed after adding income and expense transactions with same value")

        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec()
            
