from PySide6.QtCore import QTimer

from tests.tests_toolkit import DBTestCase, qsleep

from AppObjects.session import Session
from AppManagement.account import load_account_data, clear_accounts_layout, load_accounts

from GUI.windows.main_window import MainWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.account import AddAccountWindow, RenameAccountWindow
from GUI.windows.messages import Messages




class TestAccount(DBTestCase):

    def open_settings(self, func):
        QTimer.singleShot(100, func)
        MainWindow.settings.click()


    def test_1_account_adding(self):
        def open_add_window():
            def add_account():
                AddAccountWindow.account_name.setText("Second test user")
                AddAccountWindow.current_balance.setText("100")

                def check_account_existance():
                    self.assertTrue(Session.db.account_exists("Second test user"), "Second test user hasn't been created")
                    SettingsWindow.window.done(1)
                QTimer.singleShot(100, check_account_existance)
                AddAccountWindow.button.click()

            QTimer.singleShot(100, add_account)
            SettingsWindow.add_account.click()

        self.open_settings(open_add_window)
        qsleep(500)           
    

    def test_2_account_rename(self):
        def open_rename_window():
            def rename_account():
                RenameAccountWindow.new_account_name.setText("Test user rename test")

                def check_account_name():
                    self.assertEqual(Session.db.get_account().name, "Test user rename test", "Test user hasn't been renamed")
                QTimer.singleShot(100, check_account_name)
                RenameAccountWindow.button.click()

                qsleep(300)

                RenameAccountWindow.new_account_name.setText("Test user")
                def rename_back():
                    self.assertEqual(Session.db.get_account().name, "Test user", "Test user hasn't been renamed back")
                    SettingsWindow.window.done(0)
                QTimer.singleShot(100, rename_back)
                RenameAccountWindow.button.click()

            QTimer.singleShot(100, rename_account)
            SettingsWindow.rename_account.click()

        self.open_settings(open_rename_window)

        qsleep(700)
    

    def test_3_account_deletion(self):
        Session.account_name = "Second test user"
        Session.db.create_account(Session.account_name, 100)

        clear_accounts_layout()
        load_accounts()
        load_account_data(Session.account_name)

        def delete_account():
            def confirm_deletion():
                Messages.delete_account_warning.ok_button.click()
                def check_deletion():
                    self.assertFalse(Session.db.account_exists("Second test user"), "Account hasn't been removed")
                    self.assertEqual(Session.account_name, "Test user", "Test user hasn't been loaded after Second test user deletion")
                    SettingsWindow.window.done(0)
                QTimer.singleShot(200, check_deletion)

            QTimer.singleShot(100, confirm_deletion)
            SettingsWindow.delete_account.click()

        self.open_settings(delete_account)
        qsleep(500)



        
        