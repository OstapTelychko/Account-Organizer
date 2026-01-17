from PySide6.QtCore import QTimer
from datetime import date

from tests.tests_toolkit import DBTestCase, OutOfScopeTestCase, qsleep

from languages import LanguageStructure
from backend.models import Category
from GUI.gui_constants import app
from AppManagement.shortcuts.shortcuts_actions import move_to_next_category

from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.logger import get_logger


logger = get_logger(__name__)

class TestCategory(DBTestCase, OutOfScopeTestCase):
    """Test category management in the application."""

    def test_1_category_creation(self) -> None:
        """Test adding category to the application."""

        app_core = AppCore.instance()
        def _add_category(name:str) -> None:
            """Set category name and click add button."""
            
            WindowsRegistry.AddCategoryWindow.category_name.setText(name)
            self.click_on_widget(WindowsRegistry.AddCategoryWindow.button)

        QTimer.singleShot(100, self.catch_failure(lambda: _add_category("Test incomes creation category")))
        self.click_on_widget(WindowsRegistry.MainWindow.add_incomes_category)
        self.assertTrue(
            app_core.db.category_query.category_exists("Test incomes creation category", "Incomes"),
            "Incomes category hasn't been created"
        )

        QTimer.singleShot(100, self.catch_failure(lambda: _add_category("Test expenses creation category")))
        WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(1)
        self.click_on_widget(WindowsRegistry.MainWindow.add_expenses_category)
        self.assertTrue(
            app_core.db.category_query.category_exists("Test expenses creation category", "Expenses"),
            "Expenses category hasn't been created"
        )
        
        qsleep(500)
    

    def test_2_category_deletion(self) -> None:
        """Test deleting category from the application."""

        app_core = AppCore.instance()
        income_category_name = self.income_category.name
        expenses_category_name = self.expenses_category.name

        for category in app_core.categories.copy().values():
            self.select_correct_tab(category)

            def _delete_category() -> None:
                """Click delete button and confirm deletion."""

                QTimer.singleShot(
                    100,
                    lambda:self.click_on_widget(WindowsRegistry.Messages.delete_category_confirmation.ok_button)
                )
                self.click_on_widget(WindowsRegistry.CategorySettingsWindow.delete_category)

            QTimer.singleShot(100, self.catch_failure(_delete_category))
            self.click_on_widget(category.settings)

        self.assertFalse(
            app_core.db.category_query.category_exists(income_category_name, "Incomes"),
            "Income category hasn't been deleted"
        )
        self.assertFalse(
            app_core.db.category_query.category_exists(expenses_category_name, "Expenses"),
            "Expense category hasn't been deleted"
        )

        qsleep(500)
    

    def test_3_category_rename(self) -> None:
        """Test renaming category in the application."""

        app_core = AppCore.instance()
        income_category_name = self.income_category.name
        expenses_category_name = self.expenses_category.name

        for category in app_core.categories.copy().values():
            self.select_correct_tab(category)

            def _open_settings() -> None:
                """Click button that show rename category window."""

                def _rename_category() -> None:
                    """Set new category name and click rename button."""

                    WindowsRegistry.RenameCategoryWindow.new_category_name.setText(f"{category.name} rename test")
                    self.click_on_widget(WindowsRegistry.RenameCategoryWindow.button)

                QTimer.singleShot(100, self.catch_failure(_rename_category))
                self.click_on_widget(WindowsRegistry.CategorySettingsWindow.rename_category)

            QTimer.singleShot(100, self.catch_failure(_open_settings))
            self.click_on_widget(category.settings)

        with app_core.db.session_factory() as session:
            with session.begin():
                income_category_exists = bool(session.query(Category).filter_by(name=income_category_name+" rename test").first())
                expense_category_exists = bool(session.query(Category).filter_by(name=expenses_category_name+" rename test").first())
                
        self.assertTrue(income_category_exists, "Income category hasn't been renamed")
        self.assertTrue(expense_category_exists, "Expense category hasn't been renamed")

        qsleep(500)
    

    def test_4_category_position_change(self) -> None:
        """Test changing category position in the application."""

        app_core = AppCore.instance()
        app_core.db.category_query.create_category("Second "+self.income_category.name, "Incomes", 1)
        app_core.db.category_query.create_category("Second "+self.expenses_category.name, "Expenses", 1)

        for category in app_core.categories.copy().values():
            self.select_correct_tab(category)

            def _open_settings() -> None:
                """Click button that show change category position window."""

                def _change_position() -> None:
                    """Set new category position and click change button."""

                    WindowsRegistry.ChangeCategoryPositionWindow.new_position.setText("1")
                    self.click_on_widget(WindowsRegistry.ChangeCategoryPositionWindow.enter_new_position)

                QTimer.singleShot(100, self.catch_failure(_change_position))
                self.click_on_widget(WindowsRegistry.CategorySettingsWindow.change_category_position)

            QTimer.singleShot(100, self.catch_failure(_open_settings))
            self.click_on_widget(category.settings)
        
        income_category = app_core.db.category_query.get_category(self.income_category.name, "Incomes")
        second_income_category = app_core.db.category_query.get_category("Second "+self.income_category.name, "Incomes")
        expenses_category = app_core.db.category_query.get_category(self.expenses_category.name, "Expenses")
        second_expenses_category = app_core.db.category_query.get_category("Second "+self.expenses_category.name, "Expenses")

        if income_category is None or second_income_category is None or expenses_category is None or second_expenses_category is None:
            logger.error("Just created categories not found in the database")
            raise ValueError("Just created categories not found in the database")

        self.assertEqual(income_category.position, 1, "Income category hasn't changed position to 1")
        self.assertEqual(second_income_category.position, 0, "Income category hasn't changed position to 0")
        self.assertEqual(expenses_category.position, 1, "Expenses category hasn't changed position to 1")
        self.assertEqual(second_expenses_category.position, 0, "Expenses category hasn't changed position to 1")

        qsleep(500)
    

    def test_5_copy_month_transactions(self) -> None:
        """Test copying monthly transactions to the clipboard."""

        def check_single_category() -> None:
            """Check copying monthly transactions for single category."""

            def _copy_transactions() -> None:
                """Click copy transactions button and check if transactions are copied to the clipboard."""

                def _check_copied_transactions() -> None:
                    """Check if transactions are copied to the clipboard."""

                    if category.type == "Incomes":
                        transaction_type = "income"
                    else:
                        transaction_type = "expenses"

                    expected_transactions = f"\t{LanguageStructure.Transactions.get_translation(2)}\t{LanguageStructure.Transactions.get_translation(1)}\t{LanguageStructure.Transactions.get_translation(0)}\t\t{LanguageStructure.Months.get_translation(app_core.current_month)}\t{app_core.current_year}\n"
                    expected_transactions += f"0\t1000.0\t\t{date.today().day}\tTest {transaction_type} transaction\n"

                    self.assertEqual(
                        expected_transactions, app.clipboard().text(),
                        f"Monthly transaction hasn't been copied. Clipboard text {app.clipboard().text()}"
                    )
                    WindowsRegistry.CategorySettingsWindow.done(1)

                QTimer.singleShot(1000, self.catch_failure(_check_copied_transactions))
                self.click_on_widget(WindowsRegistry.CategorySettingsWindow.copy_transactions)

            QTimer.singleShot(500, self.catch_failure(_copy_transactions))
            self.click_on_widget(category.settings)

        app_core = AppCore.instance()
        income_categories, expense_categories = self.get_incomes_and_expenses_categories()

        WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(0)
        for category in income_categories:
            check_single_category()
            move_to_next_category()
            qsleep(500)
        
        WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(1)
        for category in expense_categories:
            check_single_category()
            move_to_next_category()
            qsleep(500)

        qsleep(1700)

