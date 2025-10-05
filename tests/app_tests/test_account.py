from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtCore import QTimer

from tests.tests_toolkit import DBTestCase, OutOfScopeTestCase, qsleep

from AppObjects.app_core import AppCore
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
        self.click_on_widget(WindowsRegistry.MainWindow.settings)


    def test_1_account_adding(self) -> None:
        """Test adding account to the application."""

        def _open_add_window() -> None:
            """Click button that show add account window."""

            def _add_account() -> None:
                """Fill account data and click add button."""

                WindowsRegistry.AddAccountWindow.account_name.setText("Second test user")
                WindowsRegistry.AddAccountWindow.current_balance.setText("100")

                def _check_account_existence() -> None:
                    """Check if account exists in the database."""

                    self.assertTrue(
                        AppCore.instance().db.account_query.account_exists("Second test user"),
                        "Second test user hasn't been created"
                    )
                    WindowsRegistry.SettingsWindow.done(1)
                QTimer.singleShot(100, self.catch_failure(_check_account_existence))
                self.click_on_widget(WindowsRegistry.AddAccountWindow.button)

            QTimer.singleShot(100, self.catch_failure(_add_account))
            self.click_on_widget(WindowsRegistry.SettingsWindow.add_account)

        self.open_settings(_open_add_window)
        qsleep(500)           
    

    def test_2_account_rename(self) -> None:
        """Test renaming account."""

        app_core = AppCore.instance()
        def _open_rename_window() -> None:
            """Click button that show rename account window."""

            def _rename_account() -> None:
                """Set new account name and click rename button."""

                WindowsRegistry.RenameAccountWindow.new_account_name.setText("Test user rename test")
                QTimer.singleShot(100, lambda: self.assertEqual(
                    app_core.db.account_query.get_account().name,
                    "Test user rename test", "Test user hasn't been renamed"
                ))
                self.click_on_widget(WindowsRegistry.RenameAccountWindow.button)

                qsleep(300)
                WindowsRegistry.SettingsWindow.done(0)

            QTimer.singleShot(100, self.catch_failure(_rename_account))
            self.click_on_widget(WindowsRegistry.SettingsWindow.rename_account)

        self.open_settings(_open_rename_window)

        WindowsRegistry.MainWindow.mini_calculator_label.setText("")
        def _rename_back() -> None:
            """Rename account back to original name. So it doesn't affect other tests."""

            def _rename() -> None:
                """Set account name back and click rename button."""
                WindowsRegistry.RenameAccountWindow.new_account_name.setText("Test user")
                QTimer.singleShot(100, lambda: self.assertEqual(
                    app_core.db.account_query.get_account().name,
                    "Test user",
                    "Test user hasn't been renamed back"
                ))
                self.click_on_widget(WindowsRegistry.RenameAccountWindow.button)
                WindowsRegistry.SettingsWindow.done(0)

            QTimer.singleShot(100, self.catch_failure(_rename))
            self.click_on_widget(WindowsRegistry.SettingsWindow.rename_account)

        self.open_settings(_rename_back)
        qsleep(1000)
    

    def test_3_account_deletion(self) -> None:
        """Test deleting account."""

        app_core = AppCore.instance()
        app_core.config.account_name = "Second test user"
        app_core.db.create_account(app_core.config.account_name, 100)

        clear_accounts_layout()
        load_accounts()
        load_account_data(app_core.config.account_name)

        def _delete_account() -> None:
            """Click button that show delete account window."""

            def _confirm_deletion() -> None:
                """Click delete account button."""

                self.click_on_widget(WindowsRegistry.Messages.delete_account_warning.ok_button)
                def _check_deletion() -> None:
                    """Check if account has been deleted."""

                    self.assertFalse(
                        app_core.db.account_query.account_exists("Second test user"),
                        "Account hasn't been removed"
                    )
                    self.assertEqual(
                        app_core.config.account_name,
                        "Test user",
                        "Test user hasn't been loaded after Second test user deletion"
                    )
                    WindowsRegistry.SettingsWindow.done(0)
                QTimer.singleShot(200, self.catch_failure(_check_deletion))

            QTimer.singleShot(100, self.catch_failure(_confirm_deletion))
            self.click_on_widget(WindowsRegistry.SettingsWindow.delete_account)

        self.open_settings(_delete_account)
        qsleep(500)



        
        