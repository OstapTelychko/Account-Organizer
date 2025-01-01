import shutil
import os
from functools import partial
from datetime import datetime, timedelta
from PySide6.QtCore import QTimer, QEventLoop

from project_configuration import TEST_BACKUPS_DIRECTORY
from tests.tests_toolkit import DBTestCase
from AppObjects.session import Session

from AppManagement.backup_management import auto_backup

from GUI.windows.messages import Messages
from GUI.windows.backup_management import BackupManagementWindow, AutoBackupWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.main_window import MainWindow
from GUI.windows.category import AddCategoryWindow



class TestBackupsManagement(DBTestCase):

    def setUp(self):
        os.makedirs(TEST_BACKUPS_DIRECTORY, exist_ok=True)
        return super().setUp()


    def tearDown(self):
        BackupManagementWindow.backups_table.setRowCount(0)
        Session.backups.clear()
        shutil.rmtree(TEST_BACKUPS_DIRECTORY)
        return super().tearDown()


    def open_backup_management_window(self, func):
        def open_backup_management():
            QTimer.singleShot(100, func)
            SettingsWindow.backup_management.click()

        QTimer.singleShot(100, open_backup_management)
        MainWindow.settings.click()


    def test_1_create_backup(self):
        def create_backup():
            BackupManagementWindow.create_backup.click()

            def check_backup_appearance():
                self.assertEqual(
                1, BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been added to the table or more then 1 backup is added {BackupManagementWindow.backups_table.rowCount()}"
                )

                self.assertEqual(
                1, len(Session.backups),
                f"Backup hasn't been added to the session or more then 1 backup is added {len(Session.backups)}"
                )

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more then 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                )

                self.assertEqual(BackupManagementWindow.create_backup.isEnabled(), True, "Create backup button hasn't been enabled")
                
                BackupManagementWindow.window.done(0)
                SettingsWindow.window.done(0)

            self.assertEqual(BackupManagementWindow.create_backup.isEnabled(), False, "Create backup button hasn't been disabled")
            QTimer.singleShot(1000, check_backup_appearance)

        self.open_backup_management_window(create_backup)

        loop = QEventLoop()
        QTimer.singleShot(5000, loop.quit)
        loop.exec()
    

    def test_2_remove_backup(self):
        def remove_backup():
            BackupManagementWindow.create_backup.click()

            def check_no_selection():
                self.assertEqual(Messages.unselected_row.isVisible(), True, "Unselected row message hasn't been shown")
                Messages.unselected_row.ok_button.click()
            QTimer.singleShot(100, check_no_selection)
            BackupManagementWindow.delete_backup.click()

            loop = QEventLoop()
            QTimer.singleShot(1000, loop.quit)
            loop.exec()

            BackupManagementWindow.backups_table.selectRow(0)
            def check_below_min_backups():
                self.assertEqual(Messages.below_min_backups.isVisible(), True, "Below min backups message hasn't been shown")
                Messages.below_min_backups.ok_button.click()
            QTimer.singleShot(200, check_below_min_backups)
            BackupManagementWindow.delete_backup.click()

            def check_backup_deletion():
                self.assertEqual(
                0, BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been removed from the table or more then 0 backups are left {BackupManagementWindow.backups_table.rowCount()}"
                )

                self.assertEqual(
                0, len(Session.backups),
                f"Backup hasn't been removed from the session or more then 0 backups are left {len(Session.backups)}"
                )

                self.assertEqual(
                0, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been removed or more then 0 backups are left {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                )
                
                BackupManagementWindow.window.done(0)
                SettingsWindow.window.done(0)
            
            QTimer.singleShot(100, check_backup_deletion)
    
        self.open_backup_management_window(remove_backup)

        loop = QEventLoop()
        QTimer.singleShot(2000, loop.quit)
        loop.exec()
        

    def test_3_load_backup(self):
        def prepare_load_backup():
            BackupManagementWindow.create_backup.click()
            BackupManagementWindow.window.done(0)
            SettingsWindow.window.done(0)

            def add_category():
                AddCategoryWindow.category_name.setText("Test backup category name")
                def load_backup():
                    def check_no_selection():
                        self.assertEqual(Messages.unselected_row.isVisible(), True, "Unselected row message hasn't been shown")
                        Messages.unselected_row.ok_button.click()
                    QTimer.singleShot(100, check_no_selection)
                    BackupManagementWindow.load_backup.click()

                    loop = QEventLoop()
                    QTimer.singleShot(1000, loop.quit)
                    loop.exec()

                    BackupManagementWindow.backups_table.selectRow(0)

                    def check_load_confirmation():
                        self.assertEqual(Messages.load_backup_confirmation.isVisible(), True, "Load backup confirmation message hasn't been shown")

                        def check_backup_load():
                            self.assertEqual(
                            2, len(Session.categories),
                            f"Expected categories amount after backup load is 2 returned {len(Session.categories)}"
                            )

                            self.assertEqual(
                            2, len(Session.db.get_all_categories()),
                            f"Expected categories amount after backup load is 2 returned {len(Session.db.get_all_categories())}"
                            )

                            def load_newest_backup():
                                BackupManagementWindow.backups_table.selectRow(0)

                                def check_load_confirmation():
                                    self.assertEqual(Messages.load_backup_confirmation.isVisible(), True, "Load backup confirmation message hasn't been shown")
                                    Messages.load_backup_confirmation.ok_button.click()
                                QTimer.singleShot(100, check_load_confirmation)
                                BackupManagementWindow.load_backup.click()

                                def check_backup_load():
                                    self.assertEqual(
                                    3, len(Session.categories),
                                    f"Expected categories amount after backup load is 3 returned {len(Session.categories)}"
                                    )

                                    self.assertEqual(
                                    3, len(Session.db.get_all_categories()),
                                    f"Expected categories amount after backup load is 3 returned {len(Session.db.get_all_categories())}"
                                    )

                                    self.assertEqual(BackupManagementWindow.window.isVisible(), False, "Backup management window hasn't been closed")
                                    self.assertEqual(SettingsWindow.window.isVisible(), False, "Settings window hasn't been closed")
                                QTimer.singleShot(200, check_backup_load)

                            self.open_backup_management_window(load_newest_backup)
                            loop = QEventLoop()
                            QTimer.singleShot(2000, loop.quit)
                            loop.exec()

                        QTimer.singleShot(1000, check_backup_load)
                        Messages.load_backup_confirmation.ok_button.click()

                    QTimer.singleShot(100, check_load_confirmation)
                    BackupManagementWindow.load_backup.click()

                QTimer.singleShot(200, partial(self.open_backup_management_window, load_backup))
                AddCategoryWindow.button.click()
            
            QTimer.singleShot(100, add_category)
            MainWindow.add_incomes_category.click()

        self.open_backup_management_window(prepare_load_backup)
        loop = QEventLoop()
        QTimer.singleShot(5000, loop.quit)
        loop.exec()
    

    def test_4_auto_daily_backup(self):
        Session.auto_backup_status = Session.AutoBackupStatus.DAILY
        date_now = datetime.now()
        date_minus_1_day = date_now - timedelta(days=1)

        def prepare_auto_daily_backup():
            def check_backup_appearance():
                self.assertEqual(
                1, BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been added to the table or more then 1 backup is added {BackupManagementWindow.backups_table.rowCount()}"
                )

                self.assertEqual(
                1, len(Session.backups),
                f"Backup hasn't been added to the session or more then 1 backup is added {len(Session.backups)}"
                )

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more then 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                )

                def check_no_new_backup():
                    self.assertEqual(
                    1, BackupManagementWindow.backups_table.rowCount(),
                    f"Backup have been added even though less then 1 day has passed {BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                    1, len(Session.backups),
                    f"Backup have been added even though less then 1 day has passed {len(Session.backups)}"
                    )

                    self.assertEqual(
                    1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file have been created even though less then 1 day has passed {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                QTimer.singleShot(100, check_no_new_backup)
                auto_backup()
                loop = QEventLoop()
                QTimer.singleShot(500, loop.quit)
                loop.exec()
                
                backup = Session.backups[BackupManagementWindow.backups_table.item(0, 2).text()]
                backup.timestamp = date_minus_1_day.strftime("%d-%m-%Y_%H:%M:%S")

                def check_second_backup_appearance():
                    self.assertEqual(
                    2, BackupManagementWindow.backups_table.rowCount(),
                    f"Backup during daily auto backup hasn't been added to the table or more then 2 backups are added {BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                    2, len(Session.backups),
                    f"Backup during daily auto backup hasn't been added to the session or more then 2 backups are added {len(Session.backups)}"
                    )

                    self.assertEqual(
                    2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file during daily auto backup hasn't been created or more then 2 backups are created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                    BackupManagementWindow.window.done(0)
                    SettingsWindow.window.done(0)

                QTimer.singleShot(1000, check_second_backup_appearance)
                auto_backup()

            QTimer.singleShot(1000, check_backup_appearance)
            BackupManagementWindow.create_backup.click()
        
        QTimer.singleShot(100, prepare_auto_daily_backup)
        loop = QEventLoop()
        QTimer.singleShot(5000, loop.quit)
        loop.exec()


    def test_5_auto_weekly_backup(self):
        Session.auto_backup_status = Session.AutoBackupStatus.WEEKLY
        date_now = datetime.now()
        date_minus_7_days = date_now - timedelta(days=7)

        def prepare_auto_weekly_backup():
            def check_backup_appearance():
                self.assertEqual(
                1, BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been added to the table or more then 1 backup is added {BackupManagementWindow.backups_table.rowCount()}"
                )

                self.assertEqual(
                1, len(Session.backups),
                f"Backup hasn't been added to the session or more then 1 backup is added {len(Session.backups)}"
                )

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more then 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                )

                def check_no_new_backup():
                    self.assertEqual(
                    1, BackupManagementWindow.backups_table.rowCount(),
                    f"Backup have been added even though less then 7 days has passed {BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                    1, len(Session.backups),
                    f"Backup have been added even though less then 7 days has passed {len(Session.backups)}"
                    )

                    self.assertEqual(
                    1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file have been created even though less then 7 days has passed {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                QTimer.singleShot(100, check_no_new_backup)
                auto_backup()
                loop = QEventLoop()
                QTimer.singleShot(500, loop.quit)
                loop.exec()
                
                backup = Session.backups[BackupManagementWindow.backups_table.item(0, 2).text()]
                backup.timestamp = date_minus_7_days.strftime("%d-%m-%Y_%H:%M:%S")

                def check_second_backup_appearance():
                    self.assertEqual(
                    2, BackupManagementWindow.backups_table.rowCount(),
                    f"Backup during weekly auto backup hasn't been added to the table or more then 2 backups are added {BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                    2, len(Session.backups),
                    f"Backup during weekly auto backup hasn't been added to the session or more then 2 backups are added {len(Session.backups)}"
                    )

                    self.assertEqual(
                    2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file during weekly auto backup hasn't been created or more then 2 backups are created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                    BackupManagementWindow.window.done(0)
                    SettingsWindow.window.done(0)

                QTimer.singleShot(1000, check_second_backup_appearance)
                auto_backup()

            QTimer.singleShot(1000, check_backup_appearance)
            BackupManagementWindow.create_backup.click()

        QTimer.singleShot(100, prepare_auto_weekly_backup)
        loop = QEventLoop()
        QTimer.singleShot(5000, loop.quit)
        loop.exec()


                    


            
