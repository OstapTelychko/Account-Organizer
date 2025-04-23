from PySide6.QtTest import QTest
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt, QTimer

from tests.tests_toolkit import DBTestCase, qsleep
from AppManagement.category import reset_focused_category, activate_categories
from GUI.category import load_category

from AppObjects.session import Session
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.logger import get_logger



logger = get_logger(__name__)

class TestShortcuts(DBTestCase):
    """Test shortcuts in the application."""


    def test_01_close_current_window(self) -> None:
        """Test closing current window with shortcut."""


        def _check_closure() -> None:
            QTest.keySequence(
                WindowsRegistry.AddCategoryWindow,
                QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.CLOSE_CURRENT_WINDOW]))
            qsleep(200)
            self.assertFalse(WindowsRegistry.AddCategoryWindow.isVisible(), f"Add category window should be closed after {Session.config.shortcuts[Session.config.ShortcutId.CLOSE_CURRENT_WINDOW]} shortcut.")

        QTimer.singleShot(200, _check_closure)
        WindowsRegistry.MainWindow.add_incomes_category.click()
        qsleep(200)

    
    def test_02_open_windows(self) -> None:
        """Test opening windows with shortcuts."""

        # qsleep(200)#For some reason program needs some time to start working with these shortcuts
        open_some_window_shortcuts = {Session.config.ShortcutId.OPEN_SETTINGS:WindowsRegistry.SettingsWindow, Session.config.ShortcutId.OPEN_STATISTICS:WindowsRegistry.StatisticsWindow, Session.config.ShortcutId.SWITCH_ACCOUNT:WindowsRegistry.SwitchAccountWindow}
        for shortcut_id, window in open_some_window_shortcuts.items():
            
            def _check_visibility() -> None:
                self.assertTrue(window.isVisible(), f"{window.windowTitle()} should be opened after {Session.config.shortcuts[shortcut_id]} shortcut.")
                window.done(0)
                
            QTimer.singleShot(200, _check_visibility)
            QTest.keySequence(
                WindowsRegistry.MainWindow,
                QKeySequence(Session.config.shortcuts[shortcut_id]))
            qsleep(250)
            

    def test_03_switch_to_expense(self) -> None:
        """Test switching to expense tab with shortcut."""        
        
        def _check_switch() -> None:
            self.assertEqual(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex(), 1, f"Tab should be switched to expense after {Session.config.shortcuts[Session.config.ShortcutId.SWITCH_TO_EXPENSE]} shortcut.")
            
        QTimer.singleShot(200, _check_switch)
        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SWITCH_TO_EXPENSE]))
        qsleep(200)


    def test_04_switch_to_income(self) -> None:
        """Test switching to income tab with shortcut."""        
        
        def _check_switch() -> None:
            self.assertEqual(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex(), 0, f"Tab should be switched to income after {Session.config.shortcuts[Session.config.ShortcutId.SWITCH_TO_INCOME]} shortcut.")
            
        QTimer.singleShot(200, _check_switch)
        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SWITCH_TO_INCOME]))
        qsleep(200)


    def test_05_load_previous_month(self) -> None:
        """Test loading previous month with shortcut."""        
        
        expected_previous_month = Session.current_month - 1 if Session.current_month > 1 else 12

        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.LOAD_PREVIOUS_MONTH]))
        qsleep(100)

        self.assertEqual(
            Session.current_month, expected_previous_month,
            f"Month should be switched to previous ({expected_previous_month}) after {Session.config.shortcuts[Session.config.ShortcutId.LOAD_PREVIOUS_MONTH]} shortcut not {Session.current_month} month.")


    def test_06_load_next_month(self) -> None:
        """Test loading next month with shortcut."""        
        
        expected_next_month = Session.current_month + 1 if Session.current_month < 12 else 1

        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.LOAD_NEXT_MONTH]))
        qsleep(100)

        self.assertEqual(
            Session.current_month, expected_next_month,
            f"Month should be switched to next ({expected_next_month}) after {Session.config.shortcuts[Session.config.ShortcutId.LOAD_NEXT_MONTH]} shortcut not {Session.current_month} month.")
    

    def test_07_focus_on_next_category(self) -> None:
        """Test focusing on next category with shortcut."""        

        Session.db.category_query.create_category("Second test category", "Incomes", 1)
        new_category = Session.db.category_query.get_category("Second test category", "Incomes")
        if new_category is None:
            logger.error("Just created category not found in the database")
            raise ValueError("Just created category not found in the database")

        Session.categories[new_category.id] = expected_focused_category = load_category(new_category.category_type, new_category.name, Session.db, new_category.id, 0, Session.current_year, Session.current_month)
        activate_categories()

        reset_focused_category()

        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.FOCUS_ON_NEXT_CATEGORY]))
        qsleep(100)

        if Session.focused_income_category is None:
            logger.error("Focused category is None")
            raise ValueError("Focused category is None")

        self.assertEqual(
            Session.focused_income_category, expected_focused_category,
            f"Focused category should be {expected_focused_category.name} after {Session.config.shortcuts[Session.config.ShortcutId.FOCUS_ON_NEXT_CATEGORY]} shortcut not {Session.focused_income_category.name}.")
    

    def test_08_focus_on_previous_category(self) -> None:
        """Test focusing on previous category with shortcut."""        

        Session.db.category_query.create_category("Second test category", "Incomes", 1)
        new_category = Session.db.category_query.get_category("Second test category", "Incomes")
        if new_category is None:
            logger.error("Just created category not found in the database")
            raise ValueError("Just created category not found in the database")

        Session.categories[new_category.id] = load_category(new_category.category_type, new_category.name, Session.db, new_category.id, 0, Session.current_year, Session.current_month)
        activate_categories()

        reset_focused_category()

        # Focus on next category first to make sure that focus on previous category works
        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.FOCUS_ON_NEXT_CATEGORY]))
        qsleep(100)

        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY]))
        qsleep(100)

        if Session.focused_income_category is None:
            logger.error("Focused category is None")
            raise ValueError("Focused category is None")

        self.assertEqual(
            Session.focused_income_category, Session.categories[self.income_category.id],
            f"Focused category should be {self.income_category.name} after {Session.config.shortcuts[Session.config.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY]} shortcut not {Session.focused_income_category.name}.")
        
    
    def test_09_add_transaction_to_focused_category(self) -> None:
        """Test adding transaction to focused category with shortcut."""        
        
        def _add_transaction() -> None:
            WindowsRegistry.TransactionManagementWindow.transaction_day.setText("1")
            WindowsRegistry.TransactionManagementWindow.transaction_value.setText("1000")
            WindowsRegistry.TransactionManagementWindow.button.click()
            qsleep(100)

            self.assertEqual(len(Session.db.transaction_query.get_all_transactions(self.income_category.id)), 2, f"Transaction should be added to {self.income_category.name} after {Session.config.shortcuts[Session.config.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY]} shortcut.")
        
        QTimer.singleShot(200, _add_transaction)
        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY]))
        qsleep(400)


    def test_10_select_next_and_previous_transaction(self) -> None:
        """Test selecting next and previous transaction with shortcuts."""        

        reset_focused_category()
        
        def _add_transaction() -> None:
            """Add transaction to be able to test selecting next and previous transaction."""

            WindowsRegistry.TransactionManagementWindow.transaction_day.setText("1")
            WindowsRegistry.TransactionManagementWindow.transaction_value.setText("1000")
            WindowsRegistry.TransactionManagementWindow.button.click()

        QTimer.singleShot(200, _add_transaction)
        Session.categories[self.income_category.id].add_transaction.click()

        qsleep(200)
        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SELECT_NEXT_TRANSACTION]))
        
        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SELECT_NEXT_TRANSACTION]))#I have to use shortcut twice since for the first time it selects the first transaction due to the fact that selection by init is not set
        qsleep(100)

        selected_transaction = Session.categories[self.income_category.id].table_data.currentRow()
        self.assertEqual(
            selected_transaction, 1,
            f"Next transaction should be selected after {Session.config.shortcuts[Session.config.ShortcutId.SELECT_NEXT_TRANSACTION]} shortcut not {selected_transaction} transaction.")
        
        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SELECT_PREVIOUS_TRANSACTION]))
        qsleep(100)

        selected_transaction = Session.categories[self.income_category.id].table_data.currentRow()
        self.assertEqual(
            selected_transaction, 0,
            f"Previous transaction should be selected after {Session.config.shortcuts[Session.config.ShortcutId.SELECT_PREVIOUS_TRANSACTION]} shortcut not {selected_transaction} transaction.")

        qsleep(200)


    def test_11_delete_transaction(self) -> None:
        """Test deleting transaction with shortcut."""

        reset_focused_category()     
        
        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SELECT_NEXT_TRANSACTION]))
        
        def _perform_deletion() -> None:
            """Confirm and check transaction deletion."""

            WindowsRegistry.Messages.delete_transaction_confirmation.ok_button.click()

            QTimer.singleShot(200,
                lambda: self.assertEqual(len(Session.db.transaction_query.get_all_transactions(self.income_category.id)), 0, f"Transaction should be deleted after {Session.config.shortcuts[Session.config.ShortcutId.DELETE_TRANSACTION]} shortcut."))

        QTimer.singleShot(200, _perform_deletion)
        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.DELETE_TRANSACTION]))
        qsleep(400)
    

    def test_12_edit_transaction(self) -> None:
        """Test editing transaction with shortcut."""

        reset_focused_category()

        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SELECT_NEXT_TRANSACTION]))  
        
        def _perform_edit() -> None:
            """Edit transaction and check if it was edited."""
            
            WindowsRegistry.TransactionManagementWindow.transaction_value.setText("2000")
            WindowsRegistry.TransactionManagementWindow.button.click()
            qsleep(200)

            self.assertEqual(Session.db.transaction_query.get_all_transactions(self.income_category.id)[0].value, 2000, f"Transaction should be edited after {Session.config.shortcuts[Session.config.ShortcutId.EDIT_TRANSACTION]} shortcut.")

        QTimer.singleShot(200, _perform_edit)
        QTest.keySequence(
            WindowsRegistry.MainWindow,
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.EDIT_TRANSACTION]))
        qsleep(200)
            