import shutil
import os
from functools import partial
from datetime import datetime, timedelta
from PySide6.QtCore import QTimer, QEventLoop

from languages import LANGUAGES
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
        QTimer.singleShot(3000, loop.quit)
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
                self.assertEqual(Messages.below_recommended_min_backups.isVisible(), True, "Below min backups message hasn't been shown")
                Messages.below_recommended_min_backups.ok_button.click()
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

                            QTimer.singleShot(1000, partial(self.open_backup_management_window, load_newest_backup))

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
    

    def test_4_auto_backup_status_change(self):
        def set_daily_status():
            def choose_daily_auto_backup():
                self.assertEqual(AutoBackupWindow.window.isVisible(), True, "Auto backup window hasn't been opened")

                AutoBackupWindow.daily.click()
                loop = QEventLoop()
                QTimer.singleShot(100, loop.quit)
                loop.exec()

                self.assertEqual(AutoBackupWindow.daily.isChecked(), True, "Daily auto backup hasn't been selected")
                self.assertEqual(AutoBackupWindow.weekly.isChecked(), False, "Weekly auto backup hasn't been deselected")
                self.assertEqual(AutoBackupWindow.monthly.isChecked(), False, "Monthly auto backup hasn't been deselected")

                AutoBackupWindow.save.click()
                loop = QEventLoop()
                QTimer.singleShot(200, loop.quit)
                loop.exec()

                self.assertEqual(AutoBackupWindow.window.isVisible(), False, "Auto backup window hasn't been closed")
                self.assertEqual(Session.auto_backup_status, Session.AutoBackupStatus.DAILY, "Auto backup status hasn't been changed to daily")

                translated_daily_status = LANGUAGES[Session.language]["Windows"]["Settings"]["Backup management"][7]
                self.assertNotEqual(AutoBackupWindow.current_status.text().find(translated_daily_status), -1, "Auto backup status label hasn't been changed to daily")
                self.assertNotEqual(BackupManagementWindow.auto_backup_status.text().find(translated_daily_status), -1, "Auto backup status label hasn't been changed to daily")
                BackupManagementWindow.window.done(0)
                SettingsWindow.window.done(0)

            QTimer.singleShot(100, choose_daily_auto_backup)
            BackupManagementWindow.auto_backup.click()

        self.open_backup_management_window(set_daily_status)

        loop = QEventLoop()
        QTimer.singleShot(500, loop.quit)
        loop.exec()

        def set_weekly_status():
            def choose_weekly_auto_backup():
                self.assertEqual(AutoBackupWindow.window.isVisible(), True, "Auto backup window hasn't been opened")

                AutoBackupWindow.weekly.click()
                loop = QEventLoop()
                QTimer.singleShot(100, loop.quit)
                loop.exec()

                self.assertEqual(AutoBackupWindow.daily.isChecked(), False, "Daily auto backup hasn't been deselected")
                self.assertEqual(AutoBackupWindow.weekly.isChecked(), True, "Weekly auto backup hasn't been selected")
                self.assertEqual(AutoBackupWindow.monthly.isChecked(), False, "Monthly auto backup hasn't been deselected")

                AutoBackupWindow.save.click()
                loop = QEventLoop()
                QTimer.singleShot(200, loop.quit)
                loop.exec()

                self.assertEqual(AutoBackupWindow.window.isVisible(), False, "Auto backup window hasn't been closed")
                self.assertEqual(Session.auto_backup_status, Session.AutoBackupStatus.WEEKLY, "Auto backup status hasn't been changed to weekly")

                translated_weekly_status = LANGUAGES[Session.language]["Windows"]["Settings"]["Backup management"][6]
                self.assertNotEqual(AutoBackupWindow.current_status.text().find(translated_weekly_status), -1, "Auto backup status label hasn't been changed to weekly")
                self.assertNotEqual(BackupManagementWindow.auto_backup_status.text().find(translated_weekly_status), -1, "Auto backup status label hasn't been changed to weekly")
                BackupManagementWindow.window.done(0)
                SettingsWindow.window.done(0)

            QTimer.singleShot(100, choose_weekly_auto_backup)
            BackupManagementWindow.auto_backup.click()

        self.open_backup_management_window(set_weekly_status)

        loop = QEventLoop()
        QTimer.singleShot(500, loop.quit)
        loop.exec()

        def set_monthly_status():
            def choose_monthly_auto_backup():
                self.assertEqual(AutoBackupWindow.window.isVisible(), True, "Auto backup window hasn't been opened")

                AutoBackupWindow.monthly.click()
                loop = QEventLoop()
                QTimer.singleShot(100, loop.quit)
                loop.exec()

                self.assertEqual(AutoBackupWindow.daily.isChecked(), False, "Daily auto backup hasn't been deselected")
                self.assertEqual(AutoBackupWindow.weekly.isChecked(), False, "Weekly auto backup hasn't been deselected")
                self.assertEqual(AutoBackupWindow.monthly.isChecked(), True, "Monthly auto backup hasn't been selected")

                AutoBackupWindow.save.click()
                loop = QEventLoop()
                QTimer.singleShot(200, loop.quit)
                loop.exec()

                self.assertEqual(AutoBackupWindow.window.isVisible(), False, "Auto backup window hasn't been closed")
                self.assertEqual(Session.auto_backup_status, Session.AutoBackupStatus.MONTHLY, "Auto backup status hasn't been changed to monthly")

                translated_monthly_status = LANGUAGES[Session.language]["Windows"]["Settings"]["Backup management"][5]
                self.assertNotEqual(AutoBackupWindow.current_status.text().find(translated_monthly_status), -1, "Auto backup status label hasn't been changed to monthly")
                self.assertNotEqual(BackupManagementWindow.auto_backup_status.text().find(translated_monthly_status), -1, "Auto backup status label hasn't been changed to monthly")
                BackupManagementWindow.window.done(0)
                SettingsWindow.window.done(0)

            QTimer.singleShot(100, choose_monthly_auto_backup)
            BackupManagementWindow.auto_backup.click()

        self.open_backup_management_window(set_monthly_status)

        loop = QEventLoop()
        QTimer.singleShot(500, loop.quit)
        loop.exec()


    def test_5_auto_daily_backup(self):
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

                QTimer.singleShot(200, check_no_new_backup)
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
                
            loop = QEventLoop()
            QTimer.singleShot(1000, loop.quit)
            loop.exec()
            QTimer.singleShot(1000, check_backup_appearance)
            BackupManagementWindow.create_backup.click()
        
        QTimer.singleShot(200, prepare_auto_daily_backup)
        loop = QEventLoop()
        QTimer.singleShot(5000, loop.quit)
        loop.exec()


    def test_6_auto_weekly_backup(self):
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

                QTimer.singleShot(200, check_no_new_backup)
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

            QTimer.singleShot(1200, check_backup_appearance)
            BackupManagementWindow.create_backup.click()

        QTimer.singleShot(100, prepare_auto_weekly_backup)
        loop = QEventLoop()
        QTimer.singleShot(5000, loop.quit)
        loop.exec()
    

    def test_7_auto_monthly_backup(self):
        Session.auto_backup_status = Session.AutoBackupStatus.MONTHLY
        date_now = datetime.now()
        date_minus_30_days = date_now - timedelta(days=30)

        def prepare_auto_monthly_backup():
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
                    f"Backup have been added even though less then 30 days has passed {BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                    1, len(Session.backups),
                    f"Backup have been added even though less then 30 days has passed {len(Session.backups)}"
                    )

                    self.assertEqual(
                    1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file have been created even though less then 30 days has passed {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                QTimer.singleShot(200, check_no_new_backup)
                auto_backup()
                loop = QEventLoop()
                QTimer.singleShot(500, loop.quit)
                loop.exec()
                
                backup = Session.backups[BackupManagementWindow.backups_table.item(0, 2).text()]
                backup.timestamp = date_minus_30_days.strftime("%d-%m-%Y_%H:%M:%S")

                def check_second_backup_appearance():
                    self.assertEqual(
                    2, BackupManagementWindow.backups_table.rowCount(),
                    f"Backup during monthly auto backup hasn't been added to the table or more then 2 backups are added {BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                    2, len(Session.backups),
                    f"Backup during monthly auto backup hasn't been added to the session or more then 2 backups are added {len(Session.backups)}"
                    )

                    self.assertEqual(
                    2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file during monthly auto backup hasn't been created or more than 2 backups are created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                    BackupManagementWindow.window.done(0)
                    SettingsWindow.window.done(0)

                QTimer.singleShot(1000, check_second_backup_appearance)
                auto_backup()

            QTimer.singleShot(1000, check_backup_appearance)
            BackupManagementWindow.create_backup.click()

        QTimer.singleShot(100, prepare_auto_monthly_backup)
        loop = QEventLoop()
        QTimer.singleShot(5000, loop.quit)
        loop.exec()


                    


            
