from PySide6.QtCore import QTimer
from tests.tests_toolkit import DBTestCase, qsleep

from languages import LanguageStructure
from backend.models import Category
from AppObjects.session import Session

from GUI.gui_constants import app
from GUI.windows.main_window import MainWindow
from GUI.windows.messages import Messages
from GUI.windows.category import AddCategoryWindow, CategorySettingsWindow, RenameCategoryWindow, ChangeCategoryPositionWindow



class TestCategory(DBTestCase):
    """Test category management in the application."""

    def test_1_category_creation(self):
        """Test adding category to the application."""

        def _add_category(name:str):
            """Set category name and click add button."""

            AddCategoryWindow.category_name.setText(name)
            AddCategoryWindow.button.click()

        QTimer.singleShot(100, lambda: _add_category("Test incomes creation category"))
        MainWindow.add_incomes_category.click()
        self.assertTrue(Session.db.category_query.category_exists("Test incomes creation category", "Incomes"), "Incomes category hasn't been created")

        QTimer.singleShot(100, lambda: _add_category("Test expenses creation category"))
        MainWindow.Incomes_and_expenses.setCurrentIndex(1)
        MainWindow.add_expenses_category.click()
        self.assertTrue(Session.db.category_query.category_exists("Test expenses creation category", "Expenses"), "Expenses category hasn't been created")
        
        qsleep(500)
    

    def test_2_category_deletion(self):
        """Test deleting category from the application."""

        income_category_name = self.income_category.name
        expenses_category_name = self.expenses_category.name

        for category in Session.categories.copy().values():
            self.select_correct_tab(category)

            def _delete_category():
                """Click delete button and confirm deletion."""

                QTimer.singleShot(100, lambda: Messages.delete_category_confirmation.ok_button.click())
                CategorySettingsWindow.delete_category.click()

            QTimer.singleShot(100, _delete_category)
            category.settings.click()

        self.assertFalse(Session.db.category_query.category_exists(income_category_name, "Incomes"), "Income category hasn't been deleted")
        self.assertFalse(Session.db.category_query.category_exists(expenses_category_name, "Expenses"), "Expense category hasn't been deleted")

        qsleep(500)
    

    def test_3_category_rename(self):
        """Test renaming category in the application."""

        income_category_name = self.income_category.name
        expenses_category_name = self.expenses_category.name

        for category in Session.categories.copy().values():
            self.select_correct_tab(category)

            def _open_settings():
                """Click button that show rename category window."""

                def _rename_category():
                    """Set new category name and click rename button."""

                    RenameCategoryWindow.new_category_name.setText(f"{category.name} rename test")
                    RenameCategoryWindow.button.click()

                QTimer.singleShot(100, _rename_category)
                CategorySettingsWindow.rename_category.click()

            QTimer.singleShot(100, _open_settings)
            category.settings.click()

        self.assertTrue(Session.db.session.query(Category).filter_by(name=income_category_name+" rename test").first(), "Income category hasn't been renamed")
        self.assertTrue(Session.db.session.query(Category).filter_by(name=expenses_category_name+" rename test").first(), "Expense category hasn't been renamed")

        qsleep(500)
    

    def test_4_category_position_change(self):
        """Test changing category position in the application."""

        Session.db.category_query.create_category("Second "+self.income_category.name, "Incomes", 1)
        Session.db.category_query.create_category("Second "+self.expenses_category.name, "Expenses", 1)

        for category in Session.categories.copy().values():
            self.select_correct_tab(category)

            def _open_settings():
                """Click button that show change category position window."""

                def _change_position():
                    """Set new category position and click change button."""

                    ChangeCategoryPositionWindow.new_position.setText("1")
                    ChangeCategoryPositionWindow.enter_new_position.click()

                QTimer.singleShot(100, _change_position)
                CategorySettingsWindow.change_category_position.click()

            QTimer.singleShot(100, _open_settings)
            category.settings.click()

        self.assertEqual(Session.db.category_query.get_category(self.income_category.name, "Incomes").position, 1, "Income category hasn't changed position to 1")
        self.assertEqual(Session.db.category_query.get_category("Second "+self.income_category.name, "Incomes").position, 0, "Income category hasn't changed position to 0")
        self.assertEqual(Session.db.category_query.get_category(self.expenses_category.name, "Expenses").position, 1, "Expenses category hasn't changed position to 1")
        self.assertEqual(Session.db.category_query.get_category("Second "+self.expenses_category.name, "Expenses").position, 0, "Expenses category hasn't changed position to 1")

        qsleep(500)
    

    def test_5_copy_month_transactions(self):
        """Test copying monthly transactions to the clipboard."""

        for category in Session.categories.values():
            def _copy_transactions():
                """Click copy transactions button and check if transactions are copied to the clipboard."""

                def _check_copied_transactions():
                    """Check if transactions are copied to the clipboard."""

                    if category.type == "Incomes":
                        transaction_type = "income"
                    else:
                        transaction_type = "expenses"

                    expected_transactions = f"\t{LanguageStructure.Transactions.get_translation(2)}\t{LanguageStructure.Transactions.get_translation(1)}\t{LanguageStructure.Transactions.get_translation(0)}\t\t{LanguageStructure.Months.get_translation(Session.current_month)}\t{Session.current_year}\n"
                    expected_transactions += f"0\t1000.0\t\t1\tTest {transaction_type} transaction\n"

                    self.assertEqual(expected_transactions, app.clipboard().text(), f"Monthly transaction hasn't been copied. Clipboard text {app.clipboard().text()}")
                    CategorySettingsWindow.window.done(1)

                QTimer.singleShot(100, _check_copied_transactions)
                CategorySettingsWindow.copy_transactions.click()

            QTimer.singleShot(100, _copy_transactions)
            category.settings.click()
        
        qsleep(500)

