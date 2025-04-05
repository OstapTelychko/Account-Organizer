import shutil
import os
from functools import partial
from datetime import datetime, timedelta
from PySide6.QtCore import QTimer

from languages import LANGUAGES
from project_configuration import TEST_BACKUPS_DIRECTORY, MIN_RECOMMENDED_BACKUPS, MAX_RECOMMENDED_BACKUPS, BACKUPS_DATE_FORMAT
from tests.tests_toolkit import DBTestCase, qsleep
from AppObjects.session import Session

from AppManagement.backup_management import auto_backup

from GUI.windows.messages import Messages
from GUI.windows.backup_management import BackupManagementWindow, AutoBackupWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.main_window import MainWindow
from GUI.windows.category import AddCategoryWindow



class TestBackupsManagement(DBTestCase):

    def setUp(self):
        """Create test backups directory"""

        os.makedirs(TEST_BACKUPS_DIRECTORY, exist_ok=True)
        return super().setUp()


    def tearDown(self):
        """Remove test backups directory and clear backups list and table"""

        BackupManagementWindow.backups_table.setRowCount(0)
        Session.backups.clear()
        shutil.rmtree(TEST_BACKUPS_DIRECTORY)
        return super().tearDown()


    def open_backup_management_window(self, func):
        """Open backup management window and call function after some delay.

            Arguments
            ---------
                `func` : (function) - Function to call after opening backup management window.
        """

        def _open_backup_management():
            QTimer.singleShot(100, func)
            SettingsWindow.backup_management.click()

        QTimer.singleShot(100, _open_backup_management)
        MainWindow.settings.click()


    def test_1_create_backup(self):
        """Test creating backup in the application."""

        def _create_backup():
            """Click create backup button"""

            BackupManagementWindow.create_backup.click()

            def _check_backup_appearance():
                """Check if backup is created and added to the table"""

                self.assertEqual(
                1, BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been added to the table or more then 1 backup is added {BackupManagementWindow.backups_table.rowCount()}")

                self.assertEqual(
                1, len(Session.backups),
                f"Backup hasn't been added to the session or more then 1 backup is added {len(Session.backups)}")

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more then 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                self.assertEqual(BackupManagementWindow.create_backup.isEnabled(), True, "Create backup button hasn't been enabled")
                
                BackupManagementWindow.window.done(0)
                SettingsWindow.window.done(0)

            self.assertEqual(BackupManagementWindow.create_backup.isEnabled(), False, "Create backup button hasn't been disabled")
            QTimer.singleShot(1200, _check_backup_appearance)

        self.open_backup_management_window(_create_backup)

        qsleep(2000)
    

    def test_2_remove_backup(self):
        """Test removing backup in the application."""

        def _remove_backup():
            """Create example backup and remove it"""

            BackupManagementWindow.create_backup.click()

            def _check_no_selection():
                """Check if no backup is selected"""
                
                self.assertEqual(Messages.unselected_row.isVisible(), True, "Unselected row message hasn't been shown")
                Messages.unselected_row.ok_button.click()
            QTimer.singleShot(100, _check_no_selection)
            BackupManagementWindow.delete_backup.click()

            qsleep(5000)

            BackupManagementWindow.backups_table.selectRow(0)
            def _check_below_min_backups():
                """Check if below min backups message is shown"""

                self.assertEqual(Messages.below_recommended_min_backups.isVisible(), True, "Below min backups message hasn't been shown")
                Messages.below_recommended_min_backups.ok_button.click()
            QTimer.singleShot(200, _check_below_min_backups)
            BackupManagementWindow.delete_backup.click()

            def _check_backup_deletion():
                """Check if backup is deleted from the table and session"""

                self.assertEqual(
                0, BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been removed from the table or more then 0 backups are left {BackupManagementWindow.backups_table.rowCount()}")

                self.assertEqual(
                0, len(Session.backups),
                f"Backup hasn't been removed from the session or more then 0 backups are left {len(Session.backups)}")

                self.assertEqual(
                0, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been removed or more then 0 backups are left {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")
                
                BackupManagementWindow.window.done(0)
                SettingsWindow.window.done(0)
            
            QTimer.singleShot(500, _check_backup_deletion)
    
        self.open_backup_management_window(_remove_backup)

        qsleep(3000)
        

    def test_3_load_backup(self):
        """Test loading backup in the application."""

        def _prepare_load_backup():
            """Create new backup that doesn't have new income category and load it"""

            BackupManagementWindow.create_backup.click()
            BackupManagementWindow.window.done(0)
            SettingsWindow.window.done(0)

            def _add_category():
                """Add new income category to the session"""

                AddCategoryWindow.category_name.setText("Test backup category name")
                def _load_backup():
                    """Load backup that doesn't have new income category"""

                    def _check_no_selection():
                        """Check if no backup is selected"""

                        self.assertEqual(Messages.unselected_row.isVisible(), True, "Unselected row message hasn't been shown")
                        Messages.unselected_row.ok_button.click()
                    QTimer.singleShot(100, _check_no_selection)
                    BackupManagementWindow.load_backup.click()

                    qsleep(1000)

                    BackupManagementWindow.backups_table.selectRow(0)

                    def _check_load_confirmation():
                        """Check if load backup confirmation message is shown"""

                        self.assertEqual(Messages.load_backup_confirmation.isVisible(), True, "Load backup confirmation message hasn't been shown")

                        def _check_backup_load():
                            """Check if backup is loaded and if new income category doesn't appears"""

                            self.assertEqual(
                            2, len(Session.categories),
                            f"Expected categories amount after backup load is 2 returned {len(Session.categories)}")

                            self.assertEqual(
                            2, len(Session.db.category_query.get_all_categories()),
                            f"Expected categories amount after backup load is 2 returned {len(Session.db.category_query.get_all_categories())}")

                            def _load_newest_backup():
                                """Load automatically created backup that has new income category"""

                                BackupManagementWindow.backups_table.selectRow(0)

                                def _check_load_confirmation():
                                    """Check if load backup confirmation message is shown"""

                                    self.assertEqual(Messages.load_backup_confirmation.isVisible(), True, "Load backup confirmation message hasn't been shown")
                                    Messages.load_backup_confirmation.ok_button.click()
                                QTimer.singleShot(100, _check_load_confirmation)
                                BackupManagementWindow.load_backup.click()

                                def _check_backup_load():
                                    """Check if backup is loaded and if new income category appears"""

                                    self.assertEqual(
                                    3, len(Session.categories),
                                    f"Expected categories amount after backup load is 3 returned {len(Session.categories)}")

                                    self.assertEqual(
                                    3, len(Session.db.category_query.get_all_categories()),
                                    f"Expected categories amount after backup load is 3 returned {len(Session.db.category_query.get_all_categories())}")

                                    self.assertEqual(BackupManagementWindow.window.isVisible(), False, "Backup management window hasn't been closed")
                                    self.assertEqual(SettingsWindow.window.isVisible(), False, "Settings window hasn't been closed")
                                QTimer.singleShot(200, _check_backup_load)

                            QTimer.singleShot(1000, partial(self.open_backup_management_window, _load_newest_backup))

                        QTimer.singleShot(1000, _check_backup_load)
                        Messages.load_backup_confirmation.ok_button.click()

                    QTimer.singleShot(100, _check_load_confirmation)
                    BackupManagementWindow.load_backup.click()

                QTimer.singleShot(200, partial(self.open_backup_management_window, _load_backup))
                AddCategoryWindow.button.click()
            
            QTimer.singleShot(100, _add_category)
            MainWindow.add_incomes_category.click()

        self.open_backup_management_window(_prepare_load_backup)
        qsleep(5000)
    

    def test_4_auto_backup_status_change(self):
        """Test changing auto backup status in the application."""

        def _set_daily_status():
            """Open auto backup window to set daily status"""

            def _choose_daily_auto_backup():
                """Set daily auto backup status and check if it is set correctly"""
                
                self.assertEqual(AutoBackupWindow.window.isVisible(), True, "Auto backup window hasn't been opened")

                AutoBackupWindow.daily.click()
                qsleep(100)

                self.assertEqual(AutoBackupWindow.daily.isChecked(), True, "Daily auto backup hasn't been selected")
                self.assertEqual(AutoBackupWindow.weekly.isChecked(), False, "Weekly auto backup hasn't been deselected")
                self.assertEqual(AutoBackupWindow.monthly.isChecked(), False, "Monthly auto backup hasn't been deselected")

                AutoBackupWindow.save.click()
                qsleep(200)

                self.assertEqual(AutoBackupWindow.window.isVisible(), False, "Auto backup window hasn't been closed")
                self.assertEqual(Session.auto_backup_status, Session.AutoBackupStatus.DAILY, "Auto backup status hasn't been changed to daily")

                translated_daily_status = LANGUAGES[Session.language]["Windows"]["Settings"]["Backup management"][7]
                self.assertNotEqual(AutoBackupWindow.current_status.text().find(translated_daily_status), -1, "Auto backup status label hasn't been changed to daily")
                self.assertNotEqual(BackupManagementWindow.auto_backup_status.text().find(translated_daily_status), -1, "Auto backup status label hasn't been changed to daily")
                BackupManagementWindow.window.done(0)
                SettingsWindow.window.done(0)

            QTimer.singleShot(100, _choose_daily_auto_backup)
            BackupManagementWindow.auto_backup.click()

        self.open_backup_management_window(_set_daily_status)
        qsleep(500)

        def _set_weekly_status():
            """Open auto backup window to set weekly status"""

            def _choose_weekly_auto_backup():
                """Set weekly auto backup status and check if it is set correctly"""

                self.assertEqual(AutoBackupWindow.window.isVisible(), True, "Auto backup window hasn't been opened")

                AutoBackupWindow.weekly.click()
                qsleep(100)

                self.assertEqual(AutoBackupWindow.daily.isChecked(), False, "Daily auto backup hasn't been deselected")
                self.assertEqual(AutoBackupWindow.weekly.isChecked(), True, "Weekly auto backup hasn't been selected")
                self.assertEqual(AutoBackupWindow.monthly.isChecked(), False, "Monthly auto backup hasn't been deselected")

                AutoBackupWindow.save.click()
                qsleep(200)

                self.assertEqual(AutoBackupWindow.window.isVisible(), False, "Auto backup window hasn't been closed")
                self.assertEqual(Session.auto_backup_status, Session.AutoBackupStatus.WEEKLY, "Auto backup status hasn't been changed to weekly")

                translated_weekly_status = LANGUAGES[Session.language]["Windows"]["Settings"]["Backup management"][6]
                self.assertNotEqual(AutoBackupWindow.current_status.text().find(translated_weekly_status), -1, "Auto backup status label hasn't been changed to weekly")
                self.assertNotEqual(BackupManagementWindow.auto_backup_status.text().find(translated_weekly_status), -1, "Auto backup status label hasn't been changed to weekly")
                BackupManagementWindow.window.done(0)
                SettingsWindow.window.done(0)

            QTimer.singleShot(100, _choose_weekly_auto_backup)
            BackupManagementWindow.auto_backup.click()

        self.open_backup_management_window(_set_weekly_status)
        qsleep(500)

        def _set_monthly_status():
            """Open auto backup window to set monthly status"""

            def _choose_monthly_auto_backup():
                """Set monthly auto backup status and check if it is set correctly"""

                self.assertEqual(AutoBackupWindow.window.isVisible(), True, "Auto backup window hasn't been opened")

                AutoBackupWindow.monthly.click()
                qsleep(100)

                self.assertEqual(AutoBackupWindow.daily.isChecked(), False, "Daily auto backup hasn't been deselected")
                self.assertEqual(AutoBackupWindow.weekly.isChecked(), False, "Weekly auto backup hasn't been deselected")
                self.assertEqual(AutoBackupWindow.monthly.isChecked(), True, "Monthly auto backup hasn't been selected")

                AutoBackupWindow.save.click()
                qsleep(200)

                self.assertEqual(AutoBackupWindow.window.isVisible(), False, "Auto backup window hasn't been closed")
                self.assertEqual(Session.auto_backup_status, Session.AutoBackupStatus.MONTHLY, "Auto backup status hasn't been changed to monthly")

                translated_monthly_status = LANGUAGES[Session.language]["Windows"]["Settings"]["Backup management"][5]
                self.assertNotEqual(AutoBackupWindow.current_status.text().find(translated_monthly_status), -1, "Auto backup status label hasn't been changed to monthly")
                self.assertNotEqual(BackupManagementWindow.auto_backup_status.text().find(translated_monthly_status), -1, "Auto backup status label hasn't been changed to monthly")
                BackupManagementWindow.window.done(0)
                SettingsWindow.window.done(0)

            QTimer.singleShot(100, _choose_monthly_auto_backup)
            BackupManagementWindow.auto_backup.click()

        self.open_backup_management_window(_set_monthly_status)
        qsleep(500)


    def test_5_auto_daily_backup(self):
        """Test daily auto backup in the application."""

        Session.auto_backup_status = Session.AutoBackupStatus.DAILY
        date_now = datetime.now()
        date_minus_1_day = date_now - timedelta(days=1)

        def _prepare_auto_daily_backup():
            """Create fresh backup with current date"""

            def _check_backup_appearance():
                """Check if backup is created and added to the table"""

                self.assertEqual(
                1, BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been added to the table or more then 1 backup is added {BackupManagementWindow.backups_table.rowCount()}")

                self.assertEqual(
                1, len(Session.backups),
                f"Backup hasn't been added to the session or more then 1 backup is added {len(Session.backups)}")

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more then 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                def _check_no_new_backup():
                    """Check if no new backup is created since last backup is new"""

                    self.assertEqual(
                    1, BackupManagementWindow.backups_table.rowCount(),
                    f"Backup have been added even though less then 1 day has passed {BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    1, len(Session.backups),
                    f"Backup have been added even though less then 1 day has passed {len(Session.backups)}")

                    self.assertEqual(
                    1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file have been created even though less then 1 day has passed {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                QTimer.singleShot(200, _check_no_new_backup)
                auto_backup()
                qsleep(500)
                
                backup = Session.backups[BackupManagementWindow.backups_table.item(0, 2).text()]
                backup.timestamp = date_minus_1_day.strftime(BACKUPS_DATE_FORMAT)

                def _check_second_backup_appearance():
                    """After mocking backup timestamp check if second backup is created"""

                    self.assertEqual(
                    2, BackupManagementWindow.backups_table.rowCount(),
                    f"Backup during daily auto backup hasn't been added to the table or more then 2 backups are added {BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    2, len(Session.backups),
                    f"Backup during daily auto backup hasn't been added to the session or more then 2 backups are added {len(Session.backups)}")

                    self.assertEqual(
                    2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file during daily auto backup hasn't been created or more then 2 backups are created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                    BackupManagementWindow.window.done(0)
                    SettingsWindow.window.done(0)

                QTimer.singleShot(1000, _check_second_backup_appearance)
                auto_backup()
                
            qsleep(1000)
            QTimer.singleShot(1000, _check_backup_appearance)
            BackupManagementWindow.create_backup.click()
        
        QTimer.singleShot(200, _prepare_auto_daily_backup)
        qsleep(5000)


    def test_6_auto_weekly_backup(self):
        """Test weekly auto backup in the application."""

        Session.auto_backup_status = Session.AutoBackupStatus.WEEKLY
        date_now = datetime.now()
        date_minus_7_days = date_now - timedelta(days=7)

        def _prepare_auto_weekly_backup():
            """Create fresh backup with current date"""

            def _check_backup_appearance():
                """Check if backup is created and added to the table"""

                self.assertEqual(
                1, BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been added to the table or more then 1 backup is added {BackupManagementWindow.backups_table.rowCount()}")

                self.assertEqual(
                1, len(Session.backups),
                f"Backup hasn't been added to the session or more then 1 backup is added {len(Session.backups)}")

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more then 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                def _check_no_new_backup():
                    """Check if no new backup is created since last backup is new"""

                    self.assertEqual(
                    1, BackupManagementWindow.backups_table.rowCount(),
                    f"Backup have been added even though less then 7 days has passed {BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    1, len(Session.backups),
                    f"Backup have been added even though less then 7 days has passed {len(Session.backups)}")

                    self.assertEqual(
                    1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file have been created even though less then 7 days has passed {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                QTimer.singleShot(200, _check_no_new_backup)
                auto_backup()
                qsleep(500)
                
                backup = Session.backups[BackupManagementWindow.backups_table.item(0, 2).text()]
                backup.timestamp = date_minus_7_days.strftime(BACKUPS_DATE_FORMAT)

                def _check_second_backup_appearance():
                    """After mocking backup timestamp check if second backup is created"""

                    self.assertEqual(
                    2, BackupManagementWindow.backups_table.rowCount(),
                    f"Backup during weekly auto backup hasn't been added to the table or more then 2 backups are added {BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    2, len(Session.backups),
                    f"Backup during weekly auto backup hasn't been added to the session or more then 2 backups are added {len(Session.backups)}")

                    self.assertEqual(
                    2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file during weekly auto backup hasn't been created or more then 2 backups are created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                    BackupManagementWindow.window.done(0)
                    SettingsWindow.window.done(0)

                QTimer.singleShot(1000, _check_second_backup_appearance)
                auto_backup()

            QTimer.singleShot(1200, _check_backup_appearance)
            BackupManagementWindow.create_backup.click()

        QTimer.singleShot(100, _prepare_auto_weekly_backup)
        qsleep(5000)
    

    def test_7_auto_monthly_backup(self):
        """Test monthly auto backup in the application."""

        Session.auto_backup_status = Session.AutoBackupStatus.MONTHLY
        date_now = datetime.now()
        date_minus_30_days = date_now - timedelta(days=30)

        def _prepare_auto_monthly_backup():
            """Create fresh backup with current date"""

            def _check_backup_appearance():
                """Check if backup is created and added to the table"""

                self.assertEqual(
                1, BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been added to the table or more then 1 backup is added {BackupManagementWindow.backups_table.rowCount()}")

                self.assertEqual(
                1, len(Session.backups),
                f"Backup hasn't been added to the session or more then 1 backup is added {len(Session.backups)}")

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more then 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                def _check_no_new_backup():
                    """Check if no new backup is created since last backup is new"""

                    self.assertEqual(
                    1, BackupManagementWindow.backups_table.rowCount(),
                    f"Backup have been added even though less then 30 days has passed {BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    1, len(Session.backups),
                    f"Backup have been added even though less then 30 days has passed {len(Session.backups)}")

                    self.assertEqual(
                    1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file have been created even though less then 30 days has passed {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                QTimer.singleShot(200, _check_no_new_backup)
                auto_backup()
                qsleep(500)
                
                backup = Session.backups[BackupManagementWindow.backups_table.item(0, 2).text()]
                backup.timestamp = date_minus_30_days.strftime(BACKUPS_DATE_FORMAT)

                def _check_second_backup_appearance():
                    """After mocking backup timestamp check if second backup is created"""

                    self.assertEqual(
                    2, BackupManagementWindow.backups_table.rowCount(),
                    f"Backup during monthly auto backup hasn't been added to the table or more then 2 backups are added {BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    2, len(Session.backups),
                    f"Backup during monthly auto backup hasn't been added to the session or more then 2 backups are added {len(Session.backups)}")

                    self.assertEqual(
                    2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file during monthly auto backup hasn't been created or more than 2 backups are created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                    BackupManagementWindow.window.done(0)
                    SettingsWindow.window.done(0)

                QTimer.singleShot(1000, _check_second_backup_appearance)
                auto_backup()

            QTimer.singleShot(1000, _check_backup_appearance)
            BackupManagementWindow.create_backup.click()

        QTimer.singleShot(100, _prepare_auto_monthly_backup)
        qsleep(5000)


    def test_8_check_max_backups_change(self):
        """Test changing max backups amount in the application."""

        init_max_backups = Session.max_backups

        def _open_auto_backup_settings():
            """Open auto backup window to set new max backups amount"""

            def _set_new_max_backups():
                """Set new max backups amount and check if it is set correctly"""

                def _check_no_change():
                    """Check if no change is made to max backups amount after clicking save without changing anything"""

                    self.assertEqual(
                    init_max_backups, Session.max_backups,
                    f"Expected max backups amount in session is {init_max_backups} returned {Session.max_backups}")

                    Session.load_user_config()
                    self.assertEqual(
                    init_max_backups, Session.max_backups,
                    f"Expected max backups amount in user config is {init_max_backups} returned {Session.max_backups}")

                    self.assertNotEqual(
                    -1, AutoBackupWindow.max_backups_label.text().find(str(init_max_backups)),
                    f"Expected max backups amount in label is {init_max_backups} returned {AutoBackupWindow.max_backups_label.text()}")

                QTimer.singleShot(100, _check_no_change)
                AutoBackupWindow.save.click()

                def _check_below_min_backups():
                    """Check if below min backups message is shown"""

                    self.assertEqual(Messages.below_recommended_min_backups.isVisible(), True, "Below min backups message hasn't been shown")
                    Messages.below_recommended_min_backups.ok_button.click()
                
                if MIN_RECOMMENDED_BACKUPS > 1:
                    QTimer.singleShot(200, _check_below_min_backups)
                    AutoBackupWindow.max_backups.setText(str(MIN_RECOMMENDED_BACKUPS - 1))
                    AutoBackupWindow.save.click()
                    qsleep(500)
                
                def _check_above_max_backups():
                    """Check if above max backups message is shown"""

                    self.assertEqual(Messages.above_recommended_max_backups.isVisible(), True, "Above max backups message hasn't been shown")
                    Messages.above_recommended_max_backups.ok_button.click()
                
                QTimer.singleShot(200, _check_above_max_backups)
                AutoBackupWindow.max_backups.setText(str(MAX_RECOMMENDED_BACKUPS + 1))
                AutoBackupWindow.save.click()
                qsleep(500)

                def _check_max_backups_change():
                    """Check if max backups amount is changed correctly"""

                    self.assertEqual(
                    3, Session.max_backups,
                    f"Expected max backups amount in session is 3 returned {Session.max_backups}")

                    Session.load_user_config()
                    self.assertEqual(
                    3, Session.max_backups,
                    f"Expected max backups amount in user config is 3 returned {Session.max_backups}")
                    
                    self.assertNotEqual(
                    -1, AutoBackupWindow.max_backups_label.text().find("3"),
                    f"Expected max backups amount in label is 3 returned {AutoBackupWindow.max_backups_label.text()}")

                    AutoBackupWindow.window.done(0)
                    BackupManagementWindow.window.done(0)
                    SettingsWindow.window.done(0)

                QTimer.singleShot(200, _check_max_backups_change)
                AutoBackupWindow.max_backups.setText("3")
                AutoBackupWindow.save.click()

            QTimer.singleShot(100, _set_new_max_backups)
            BackupManagementWindow.auto_backup.click()
            
        self.open_backup_management_window(_open_auto_backup_settings)
        qsleep(1000)

                    


            
