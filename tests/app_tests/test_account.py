from PySide6.QtCore import QTimer, QEventLoop

from tests.tests_toolkit import DBTestCase, OK_BUTTON

from AppObjects.session import Session
from AppManagement.account import load_account_data

from GUI.windows.main_window import MainWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.account import AddAccountWindow, RenameAccountWindow
from GUI.windows.messages import Messages




class TestAccount(DBTestCase):

    def open_settings(self, func):
        QTimer.singleShot(100, func)
        MainWindow.settings.click()


    def test_account_adding(self):
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
        loop = QEventLoop()
        QTimer.singleShot(500, loop.quit)
        loop.exec()            
    

    def test_account_rename(self):
        def open_rename_window():
            def rename_account():
                RenameAccountWindow.new_account_name.setText("Test user rename test")

                def check_account_name():
                    self.assertEqual(Session.db.get_account().name, "Test user rename test", "Test user hasn't been renamed")
                    SettingsWindow.window.done(0)
                QTimer.singleShot(100, check_account_name)
                RenameAccountWindow.button.click()

            QTimer.singleShot(100, rename_account)
            SettingsWindow.rename_account.click()

        self.open_settings(open_rename_window)

        loop = QEventLoop()
        QTimer.singleShot(500, loop.quit)
        loop.exec()
        Session.db.rename_account("Test user")
    

    def test_account_deletion(self):
        Session.account_name = "Second test user"
        Session.db.create_account(Session.account_name, 100)

        Session.accounts_list.append(Session.account_name)
        Session.switch_account = False
        SettingsWindow.accounts.clear()

        Session.switch_account = False
        SettingsWindow.accounts.addItems(Session.accounts_list)

        Session.switch_account = False
        load_account_data(Session.account_name)
        SettingsWindow.accounts.setCurrentText(Session.account_name)

        def delete_account():
            def confirm_deletion():
                Messages.delete_account_warning.button(OK_BUTTON).click()
                def check_deletion():
                    self.assertFalse(Session.db.account_exists("Second test user"), "Account hasn't been removed")
                    self.assertEqual(Session.account_name, "Test user", "Test user hasn't been loaded after Second test user deletion")
                    SettingsWindow.window.done(1)
                QTimer.singleShot(100, check_deletion)

            QTimer.singleShot(100, confirm_deletion)
            SettingsWindow.delete_account.click()

        self.open_settings(delete_account)
        loop = QEventLoop()
        QTimer.singleShot(500, loop.quit)
        loop.exec()



        
        