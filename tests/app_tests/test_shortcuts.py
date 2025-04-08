from PySide6.QtTest import QTest
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt, QTimer

from tests.tests_toolkit import DBTestCase, qsleep
from AppObjects.session import Session
from AppManagement.category import reset_focused_category, activate_categories

from GUI.windows.main_window import MainWindow
from GUI.windows.category import AddCategoryWindow
from GUI.windows.account import SwitchAccountWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.statistics import StatisticsWindow
from GUI.windows.transaction import TransactionManagementWindow
from GUI.windows.messages import Messages
from GUI.category import load_category




class TestShortcuts(DBTestCase):
    """Test shortcuts in the application."""


    def test_01_close_current_window(self):
        """Test closing current window with shortcut."""


        def _check_closure():
            QTest.keySequence(
                AddCategoryWindow.window,
                QKeySequence(Session.shortcuts[Session.ShortcutId.CLOSE_CURRENT_WINDOW]))
            qsleep(200)
            self.assertFalse(AddCategoryWindow.window.isVisible(), f"Add category window should be closed after {Session.shortcuts[Session.ShortcutId.CLOSE_CURRENT_WINDOW]} shortcut.")

        QTimer.singleShot(200, _check_closure)
        MainWindow.add_incomes_category.click()
        qsleep(200)

    
    def test_02_open_windows(self):
        """Test opening windows with shortcuts."""

        # qsleep(200)#For some reason program needs some time to start working with these shortcuts
        open_some_window_shortcuts = {Session.ShortcutId.OPEN_SETTINGS:SettingsWindow.window, Session.ShortcutId.OPEN_STATISTICS:StatisticsWindow.window, Session.ShortcutId.SWITCH_ACCOUNT:SwitchAccountWindow.window}
        for shortcut_id, window in open_some_window_shortcuts.items():
            
            def _check_visibility():
                self.assertTrue(window.isVisible(), f"{window.windowTitle()} should be opened after {Session.shortcuts[shortcut_id]} shortcut.")
                window.done(0)
                
            QTimer.singleShot(200, _check_visibility)
            QTest.keySequence(
                MainWindow.window,
                QKeySequence(Session.shortcuts[shortcut_id]))
            qsleep(250)
            

    def test_03_switch_to_expense(self):
        """Test switching to expense tab with shortcut."""        
        
        def _check_switch():
            self.assertEqual(MainWindow.Incomes_and_expenses.currentIndex(), 1, f"Tab should be switched to expense after {Session.shortcuts[Session.ShortcutId.SWITCH_TO_EXPENSE]} shortcut.")
            
        QTimer.singleShot(200, _check_switch)
        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.SWITCH_TO_EXPENSE]))
        qsleep(200)


    def test_04_switch_to_income(self):
        """Test switching to income tab with shortcut."""        
        
        def _check_switch():
            self.assertEqual(MainWindow.Incomes_and_expenses.currentIndex(), 0, f"Tab should be switched to income after {Session.shortcuts[Session.ShortcutId.SWITCH_TO_INCOME]} shortcut.")
            
        QTimer.singleShot(200, _check_switch)
        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.SWITCH_TO_INCOME]))
        qsleep(200)


    def test_05_load_previous_month(self):
        """Test loading previous month with shortcut."""        
        
        expected_previous_month = Session.current_month - 1 if Session.current_month > 1 else 12

        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.LOAD_PREVIOUS_MONTH]))
        qsleep(100)

        self.assertEqual(
            Session.current_month, expected_previous_month,
            f"Month should be switched to previous ({expected_previous_month}) after {Session.shortcuts[Session.ShortcutId.LOAD_PREVIOUS_MONTH]} shortcut not {Session.current_month} month.")


    def test_06_load_next_month(self):
        """Test loading next month with shortcut."""        
        
        expected_next_month = Session.current_month + 1 if Session.current_month < 12 else 1

        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.LOAD_NEXT_MONTH]))
        qsleep(100)

        self.assertEqual(
            Session.current_month, expected_next_month,
            f"Month should be switched to next ({expected_next_month}) after {Session.shortcuts[Session.ShortcutId.LOAD_NEXT_MONTH]} shortcut not {Session.current_month} month.")
    

    def test_07_focus_on_next_category(self):
        """Test focusing on next category with shortcut."""        

        Session.db.category_query.create_category("Second test category", "Incomes", 1)
        new_category = Session.db.category_query.get_category("Second test category", "Incomes")
        Session.categories[new_category.id] = expected_focused_category = load_category(new_category.category_type, new_category.name, Session.db, new_category.id, 0, Session.current_year, Session.current_month, Session.language)
        activate_categories()

        reset_focused_category()

        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.FOCUS_ON_NEXT_CATEGORY]))
        qsleep(100)

        self.assertEqual(
            Session.focused_income_category, expected_focused_category,
            f"Focused category should be {expected_focused_category.name} after {Session.shortcuts[Session.ShortcutId.FOCUS_ON_NEXT_CATEGORY]} shortcut not {Session.focused_income_category.name}.")
    

    def test_08_focus_on_previous_category(self):
        """Test focusing on previous category with shortcut."""        

        Session.db.category_query.create_category("Second test category", "Incomes", 1)
        new_category = Session.db.category_query.get_category("Second test category", "Incomes")
        Session.categories[new_category.id] = load_category(new_category.category_type, new_category.name, Session.db, new_category.id, 0, Session.current_year, Session.current_month, Session.language)
        activate_categories()

        reset_focused_category()

        # Focus on next category first to make sure that focus on previous category works
        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.FOCUS_ON_NEXT_CATEGORY]))
        qsleep(100)

        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY]))
        qsleep(100)

        self.assertEqual(
            Session.focused_income_category, Session.categories[self.income_category.id],
            f"Focused category should be {self.income_category.name} after {Session.shortcuts[Session.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY]} shortcut not {Session.focused_income_category.name}.")
        
    
    def test_09_add_transaction_to_focused_category(self):
        """Test adding transaction to focused category with shortcut."""        
        
        def _add_transaction():
            TransactionManagementWindow.transaction_day.setText("1")
            TransactionManagementWindow.transaction_value.setText("1000")
            TransactionManagementWindow.button.click()
            qsleep(100)

            self.assertEqual(len(Session.db.transaction_query.get_all_transactions(self.income_category.id)), 2, f"Transaction should be added to {self.income_category.name} after {Session.shortcuts[Session.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY]} shortcut.")
        
        QTimer.singleShot(200, _add_transaction)
        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY]))
        qsleep(400)


    def test_10_select_next_and_previous_transaction(self):
        """Test selecting next and previous transaction with shortcuts."""        

        reset_focused_category()
        
        def _add_transaction():
            """Add transaction to be able to test selecting next and previous transaction."""

            TransactionManagementWindow.transaction_day.setText("1")
            TransactionManagementWindow.transaction_value.setText("1000")
            TransactionManagementWindow.button.click()

        QTimer.singleShot(200, _add_transaction)
        Session.categories[self.income_category.id].add_transaction.click()

        qsleep(200)
        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.SELECT_NEXT_TRANSACTION]))
        
        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.SELECT_NEXT_TRANSACTION]))#I have to use shortcut twice since for the first time it selects the first transaction due to the fact that selection by init is not set
        qsleep(100)

        selected_transaction = Session.categories[self.income_category.id].table_data.currentRow()
        self.assertEqual(
            selected_transaction, 1,
            f"Next transaction should be selected after {Session.shortcuts[Session.ShortcutId.SELECT_NEXT_TRANSACTION]} shortcut not {selected_transaction} transaction.")
        
        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.SELECT_PREVIOUS_TRANSACTION]))
        qsleep(100)

        selected_transaction = Session.categories[self.income_category.id].table_data.currentRow()
        self.assertEqual(
            selected_transaction, 0,
            f"Previous transaction should be selected after {Session.shortcuts[Session.ShortcutId.SELECT_PREVIOUS_TRANSACTION]} shortcut not {selected_transaction} transaction.")

        qsleep(200)


    def test_11_delete_transaction(self):
        """Test deleting transaction with shortcut."""

        reset_focused_category()     
        
        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.SELECT_NEXT_TRANSACTION]))
        
        def _perform_deletion():
            """Confirm and check transaction deletion."""

            Messages.delete_transaction_confirmation.ok_button.click()

            QTimer.singleShot(200,
                lambda: self.assertEqual(len(Session.db.transaction_query.get_all_transactions(self.income_category.id)), 0, f"Transaction should be deleted after {Session.shortcuts[Session.ShortcutId.DELETE_TRANSACTION]} shortcut."))

        QTimer.singleShot(200, _perform_deletion)
        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.DELETE_TRANSACTION]))
        qsleep(400)
    

    def test_12_edit_transaction(self):
        """Test editing transaction with shortcut."""

        reset_focused_category()

        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.SELECT_NEXT_TRANSACTION]))  
        
        def _perform_edit():
            """Edit transaction and check if it was edited."""
            
            TransactionManagementWindow.transaction_value.setText("2000")
            TransactionManagementWindow.button.click()
            qsleep(200)

            self.assertEqual(Session.db.transaction_query.get_all_transactions(self.income_category.id)[0].value, 2000, f"Transaction should be edited after {Session.shortcuts[Session.ShortcutId.EDIT_TRANSACTION]} shortcut.")

        QTimer.singleShot(200, _perform_edit)
        QTest.keySequence(
            MainWindow.window,
            QKeySequence(Session.shortcuts[Session.ShortcutId.EDIT_TRANSACTION]))
        qsleep(200)
            