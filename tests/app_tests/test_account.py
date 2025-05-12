from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtCore import QTimer

from tests.tests_toolkit import DBTestCase, OutOfScopeTestCase, qsleep

from AppObjects.session import Session
from AppObjects.windows_registry import WindowsRegistry
from AppManagement.account import load_account_data, clear_accounts_layout, load_accounts

if TYPE_CHECKING:
    from typing import Callable



class TestAccount(DBTestCase, OutOfScopeTestCase):
    """Test account management in the application."""

    def open_settings(self, func:Callable[[], None]) -> None:
        """Open settings window and call function after some delay.

            Arguments
            ---------
                `func` : (function) - Function to call after opening settings window.
        """

        QTimer.singleShot(100, self.catch_failure(func))
        WindowsRegistry.MainWindow.settings.click()


    def test_1_account_adding(self) -> None:
        """Test adding account to the application."""

        def _open_add_window() -> None:
            """Click button that show add account window."""

            def _add_account() -> None:
                """Fill account data and click add button."""

                WindowsRegistry.AddAccountWindow.account_name.setText("Second test user")
                WindowsRegistry.AddAccountWindow.current_balance.setText("100")

                def _check_account_existance() -> None:
                    """Check if account exists in the database."""

                    self.assertTrue(Session.db.account_query.account_exists("Second test user"), "Second test user hasn't been created")
                    WindowsRegistry.SettingsWindow.done(1)
                QTimer.singleShot(100, self.catch_failure(_check_account_existance))
                WindowsRegistry.AddAccountWindow.button.click()

            QTimer.singleShot(100, self.catch_failure(_add_account))
            WindowsRegistry.SettingsWindow.add_account.click()

        self.open_settings(_open_add_window)
        qsleep(500)           
    

    def test_2_account_rename(self) -> None:
        """Test renaming account."""

        def _open_rename_window() -> None:
            """Click button that show rename account window."""

            def _rename_account() -> None:
                """Set new account name and click rename button."""

                WindowsRegistry.RenameAccountWindow.new_account_name.setText("Test user rename test")

                def _check_account_name() -> None:
                    """Check if account name has been changed."""

                    self.assertEqual(Session.db.account_query.get_account().name, "Test user rename test", "Test user hasn't been renamed")
                QTimer.singleShot(100, self.catch_failure(_check_account_name))
                WindowsRegistry.RenameAccountWindow.button.click()

                qsleep(300)

                WindowsRegistry.RenameAccountWindow.new_account_name.setText("Test user")
                def _rename_back() -> None:
                    """Rename account back to original name. So it doesn't affect other tests."""

                    self.assertEqual(Session.db.account_query.get_account().name, "Test user", "Test user hasn't been renamed back")
                    WindowsRegistry.SettingsWindow.done(0)
                QTimer.singleShot(100, self.catch_failure(_rename_back))
                WindowsRegistry.RenameAccountWindow.button.click()

            QTimer.singleShot(100, self.catch_failure(_rename_account))
            WindowsRegistry.SettingsWindow.rename_account.click()

        self.open_settings(_open_rename_window)

        qsleep(700)
    

    def test_3_account_deletion(self) -> None:
        """Test deleting account."""

        Session.config.account_name = "Second test user"
        Session.db.create_account(Session.config.account_name, 100)

        clear_accounts_layout()
        load_accounts()
        load_account_data(Session.config.account_name)

        def _delete_account() -> None:
            """Click button that show delete account window."""

            def _confirm_deletion() -> None:
                """Click delete account button."""

                WindowsRegistry.Messages.delete_account_warning.ok_button.click()
                def _check_deletion() -> None:
                    """Check if account has been deleted."""

                    self.assertFalse(Session.db.account_query.account_exists("Second test user"), "Account hasn't been removed")
                    self.assertEqual(Session.config.account_name, "Test user", "Test user hasn't been loaded after Second test user deletion")
                    WindowsRegistry.SettingsWindow.done(0)
                QTimer.singleShot(200, self.catch_failure(_check_deletion))

            QTimer.singleShot(100, self.catch_failure(_confirm_deletion))
            WindowsRegistry.SettingsWindow.delete_account.click()

        self.open_settings(_delete_account)
        qsleep(500)



        
        