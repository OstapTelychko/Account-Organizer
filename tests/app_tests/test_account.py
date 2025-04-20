from PySide6.QtCore import QTimer

from tests.tests_toolkit import DBTestCase, qsleep

from AppObjects.session import Session
from AppManagement.account import load_account_data, clear_accounts_layout, load_accounts

from GUI.windows.main_window import MainWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.account import AddAccountWindow, RenameAccountWindow
from GUI.windows.messages import Messages




class TestAccount(DBTestCase):
    """Test account management in the application."""

    def open_settings(self, func):
        """Open settings window and call function after some delay.

            Arguments
            ---------
                `func` : (function) - Function to call after opening settings window.
        """

        QTimer.singleShot(100, func)
        MainWindow.settings.click()


    def test_1_account_adding(self):
        """Test adding account to the application."""

        def _open_add_window():
            """Click button that show add account window."""

            def _add_account():
                """Fill account data and click add button."""

                AddAccountWindow.account_name.setText("Second test user")
                AddAccountWindow.current_balance.setText("100")

                def _check_account_existance():
                    """Check if account exists in the database."""

                    self.assertTrue(Session.db.account_query.account_exists("Second test user"), "Second test user hasn't been created")
                    SettingsWindow.window.done(1)
                QTimer.singleShot(100, _check_account_existance)
                AddAccountWindow.button.click()

            QTimer.singleShot(100, _add_account)
            SettingsWindow.add_account.click()

        self.open_settings(_open_add_window)
        qsleep(500)           
    

    def test_2_account_rename(self):
        """Test renaming account."""

        def _open_rename_window():
            """Click button that show rename account window."""

            def _rename_account():
                """Set new account name and click rename button."""

                RenameAccountWindow.new_account_name.setText("Test user rename test")

                def _check_account_name():
                    """Check if account name has been changed."""

                    self.assertEqual(Session.db.account_query.get_account().name, "Test user rename test", "Test user hasn't been renamed")
                QTimer.singleShot(100, _check_account_name)
                RenameAccountWindow.button.click()

                qsleep(300)

                RenameAccountWindow.new_account_name.setText("Test user")
                def _rename_back():
                    """Rename account back to original name. So it doesn't affect other tests."""

                    self.assertEqual(Session.db.account_query.get_account().name, "Test user", "Test user hasn't been renamed back")
                    SettingsWindow.window.done(0)
                QTimer.singleShot(100, _rename_back)
                RenameAccountWindow.button.click()

            QTimer.singleShot(100, _rename_account)
            SettingsWindow.rename_account.click()

        self.open_settings(_open_rename_window)

        qsleep(700)
    

    def test_3_account_deletion(self):
        """Test deleting account."""

        Session.config.account_name = "Second test user"
        Session.db.create_account(Session.config.account_name, 100)

        clear_accounts_layout()
        load_accounts()
        load_account_data(Session.config.account_name)

        def _delete_account():
            """Click button that show delete account window."""

            def _confirm_deletion():
                """Click delete account button."""

                Messages.delete_account_warning.ok_button.click()
                def _check_deletion():
                    """Check if account has been deleted."""

                    self.assertFalse(Session.db.account_query.account_exists("Second test user"), "Account hasn't been removed")
                    self.assertEqual(Session.config.account_name, "Test user", "Test user hasn't been loaded after Second test user deletion")
                    SettingsWindow.window.done(0)
                QTimer.singleShot(200, _check_deletion)

            QTimer.singleShot(100, _confirm_deletion)
            SettingsWindow.delete_account.click()

        self.open_settings(_delete_account)
        qsleep(500)



        
        