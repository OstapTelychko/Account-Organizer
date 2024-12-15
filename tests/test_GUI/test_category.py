from PySide6.QtCore import QTimer
from tests.tests_toolkit import DBTestCase, OK_BUTTON

from languages import LANGUAGES
from backend.models import Category
from AppObjects.session import Session

from GUI.gui_constants import app
from GUI.windows.main_window import MainWindow
from GUI.windows.messages import Messages
from GUI.windows.category import AddCategoryWindow, CategorySettingsWindow, RenameCategoryWindow, ChangeCategoryPositionWindow



class TestCategory(DBTestCase):

    def test_category_creation(self):

        def add_category(name:str):
            AddCategoryWindow.category_name.setText(name)
            AddCategoryWindow.button.click()

        QTimer.singleShot(100, lambda: add_category("Test incomes creation category"))
        MainWindow.add_incomes_category.click()
        self.assertTrue(Session.db.category_exists("Test incomes creation category", "Incomes"), "Incomes category hasn't been created")

        QTimer.singleShot(100, lambda: add_category("Test expenses creation category"))
        MainWindow.Incomes_and_expenses.setCurrentIndex(1)
        MainWindow.add_expenses_category.click()
        self.assertTrue(Session.db.category_exists("Test expenses creation category", "Expenses"), "Expenses category hasn't been created")
    

    def test_category_deletion(self):
        income_category_name = self.income_category.name
        expenses_category_name = self.expenses_category.name

        for category in Session.categories.copy().values():
            self.select_correct_tab(category)

            def delete_category():
                QTimer.singleShot(100, lambda: Messages.delete_category_confirmation.button(OK_BUTTON).click())
                CategorySettingsWindow.delete_category.click()

            QTimer.singleShot(100, delete_category)
            category.settings.click()

        self.assertFalse(Session.db.category_exists(income_category_name, "Incomes"), "Income category hasn't been deleted")
        self.assertFalse(Session.db.category_exists(expenses_category_name, "Expenses"), "Expense category hasn't been deleted")
    

    def test_category_rename(self):
        income_category_name = self.income_category.name
        expenses_category_name = self.expenses_category.name

        for category in Session.categories.copy().values():
            self.select_correct_tab(category)

            def open_settings():

                def rename_category():
                    RenameCategoryWindow.new_category_name.setText(f"{category.name} rename test")
                    RenameCategoryWindow.button.click()

                QTimer.singleShot(100, rename_category)
                CategorySettingsWindow.rename_category.click()

            QTimer.singleShot(100, open_settings)
            category.settings.click()

        self.assertTrue(Session.db.session.query(Category).filter_by(name=income_category_name+" rename test").first(), "Income category hasn't been renamed")
        self.assertTrue(Session.db.session.query(Category).filter_by(name=expenses_category_name+" rename test").first(), "Expense category hasn't been renamed")
    

    def test_category_position_change(self):
        Session.db.create_category("Second "+self.income_category.name, "Incomes", 1)
        Session.db.create_category("Second "+self.expenses_category.name, "Expenses", 1)

        for category in Session.categories.copy().values():
            self.select_correct_tab(category)

            def open_settings():
                def change_position():
                    ChangeCategoryPositionWindow.new_position.setText("1")
                    ChangeCategoryPositionWindow.enter_new_position.click()

                QTimer.singleShot(100, change_position)
                CategorySettingsWindow.change_category_position.click()

            QTimer.singleShot(100, open_settings)
            category.settings.click()

        self.assertEqual(Session.db.get_category(self.income_category.name, "Incomes").position, 1, "Income category hasn't changed position to 1")
        self.assertEqual(Session.db.get_category("Second "+self.income_category.name, "Incomes").position, 0, "Income category hasn't changed position to 0")
        self.assertEqual(Session.db.get_category(self.expenses_category.name, "Expenses").position, 1, "Expenses category hasn't changed position to 1")
        self.assertEqual(Session.db.get_category("Second "+self.expenses_category.name, "Expenses").position, 0, "Expenses category hasn't changed position to 1")
    

    def test_copy_month_transactions(self):
        for category in Session.categories.values():
            def copy_transactions():
                def check_copied_transactions():
                    if category.type == "Incomes":
                        transaction_type = "income"
                    else:
                        transaction_type = "expenses"

                    column_names = LANGUAGES[Session.language]["Account"]["Info"]
                    expected_transactions = f"\t{column_names[2]}\t{column_names[1]}\t{column_names[0]}\t\t{LANGUAGES[Session.language]['Months'][Session.current_month]}\t{Session.current_year}\n"
                    expected_transactions += f"0\t1000.0\t\t1\tTest {transaction_type} transaction\n"

                    self.assertEqual(expected_transactions, app.clipboard().text(), f"Monthly transaction hasn't been copied. Clipboard text {app.clipboard().text()}")
                    CategorySettingsWindow.window.done(1)

                QTimer.singleShot(100, check_copied_transactions)
                CategorySettingsWindow.copy_transactions.click()

            QTimer.singleShot(100, copy_transactions)
            category.settings.click()

