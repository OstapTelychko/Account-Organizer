from __future__ import annotations
from typing import TYPE_CHECKING
import shutil
import os
from functools import partial
from datetime import datetime, timedelta
from PySide6.QtCore import QTimer

from languages import LanguageStructure
from project_configuration import TEST_BACKUPS_DIRECTORY, MIN_RECOMMENDED_BACKUPS, MAX_RECOMMENDED_BACKUPS, BACKUPS_DATE_FORMAT
from tests.tests_toolkit import DBTestCase, qsleep
from AppObjects.session import Session
from AppObjects.windows_registry import WindowsRegistry

from AppManagement.backup_management import auto_backup

if TYPE_CHECKING:
    from typing import Callable



class TestBackupsManagement(DBTestCase):
    """Test backup management in the application."""

    def setUp(self) -> None:
        """Create test backups directory"""

        os.makedirs(TEST_BACKUPS_DIRECTORY, exist_ok=True)
        return super().setUp()


    def tearDown(self) -> None:
        """Remove test backups directory and clear backups list and table"""

        WindowsRegistry.BackupManagementWindow.backups_table.setRowCount(0)
        Session.backups.clear()
        shutil.rmtree(TEST_BACKUPS_DIRECTORY)
        return super().tearDown()


    def open_backup_management_window(self, func:Callable[[], None]) -> None:
        """Open backup management window and call function after some delay.

            Arguments
            ---------
                `func` : (function) - Function to call after opening backup management window.
        """

        def _open_backup_management() -> None:
            QTimer.singleShot(100, func)
            WindowsRegistry.SettingsWindow.backup_management.click()

        QTimer.singleShot(100, _open_backup_management)
        WindowsRegistry.MainWindow.settings.click()


    def test_1_create_backup(self) -> None:
        """Test creating backup in the application."""

        def _create_backup() -> None:
            """Click create backup button"""

            WindowsRegistry.BackupManagementWindow.create_backup.click()

            def _check_backup_appearance() -> None:
                """Check if backup is created and added to the table"""

                self.assertEqual(
                1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been added to the table or more then 1 backup is added {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}")

                self.assertEqual(
                1, len(Session.backups),
                f"Backup hasn't been added to the session or more then 1 backup is added {len(Session.backups)}")

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more then 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                self.assertEqual(WindowsRegistry.BackupManagementWindow.create_backup.isEnabled(), True, "Create backup button hasn't been enabled")
                
                WindowsRegistry.BackupManagementWindow.done(0)
                WindowsRegistry.SettingsWindow.done(0)

            self.assertEqual(WindowsRegistry.BackupManagementWindow.create_backup.isEnabled(), False, "Create backup button hasn't been disabled")
            QTimer.singleShot(1200, _check_backup_appearance)

        self.open_backup_management_window(_create_backup)

        qsleep(2000)
    

    def test_2_remove_backup(self) -> None:
        """Test removing backup in the application."""

        def _remove_backup() -> None:
            """Create example backup and remove it"""

            WindowsRegistry.BackupManagementWindow.create_backup.click()

            def _check_no_selection() -> None:
                """Check if no backup is selected"""
                
                self.assertEqual(WindowsRegistry.Messages.unselected_row.isVisible(), True, "Unselected row message hasn't been shown")
                WindowsRegistry.Messages.unselected_row.ok_button.click()
            QTimer.singleShot(100, _check_no_selection)
            WindowsRegistry.BackupManagementWindow.delete_backup.click()

            qsleep(5000)

            WindowsRegistry.BackupManagementWindow.backups_table.selectRow(0)
            def _check_below_min_backups() -> None:
                """Check if below min backups message is shown"""

                self.assertEqual(WindowsRegistry.Messages.below_recommended_min_backups.isVisible(), True, "Below min backups message hasn't been shown")
                WindowsRegistry.Messages.below_recommended_min_backups.ok_button.click()
            QTimer.singleShot(200, _check_below_min_backups)
            WindowsRegistry.BackupManagementWindow.delete_backup.click()

            def _check_backup_deletion() -> None:
                """Check if backup is deleted from the table and session"""

                self.assertEqual(
                0, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been removed from the table or more then 0 backups are left {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}")

                self.assertEqual(
                0, len(Session.backups),
                f"Backup hasn't been removed from the session or more then 0 backups are left {len(Session.backups)}")

                self.assertEqual(
                0, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been removed or more then 0 backups are left {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")
                
                WindowsRegistry.BackupManagementWindow.done(0)
                WindowsRegistry.SettingsWindow.done(0)
            
            QTimer.singleShot(500, _check_backup_deletion)
    
        self.open_backup_management_window(_remove_backup)

        qsleep(3000)
        

    def test_3_load_backup(self) -> None:
        """Test loading backup in the application."""

        def _prepare_load_backup() -> None:
            """Create new backup that doesn't have new income category and load it"""

            WindowsRegistry.BackupManagementWindow.create_backup.click()
            WindowsRegistry.BackupManagementWindow.done(0)
            WindowsRegistry.SettingsWindow.done(0)

            def _add_category() -> None:
                """Add new income category to the session"""

                WindowsRegistry.AddCategoryWindow.category_name.setText("Test backup category name")
                def _load_backup() -> None:
                    """Load backup that doesn't have new income category"""

                    def _check_no_selection() -> None:
                        """Check if no backup is selected"""

                        self.assertEqual(WindowsRegistry.Messages.unselected_row.isVisible(), True, "Unselected row message hasn't been shown")
                        WindowsRegistry.Messages.unselected_row.ok_button.click()
                    QTimer.singleShot(100, _check_no_selection)
                    WindowsRegistry.BackupManagementWindow.load_backup.click()

                    qsleep(1000)

                    WindowsRegistry.BackupManagementWindow.backups_table.selectRow(0)

                    def _check_load_confirmation() -> None:
                        """Check if load backup confirmation message is shown"""

                        self.assertEqual(WindowsRegistry.Messages.load_backup_confirmation.isVisible(), True, "Load backup confirmation message hasn't been shown")

                        def _check_backup_load() -> None:
                            """Check if backup is loaded and if new income category doesn't appears"""

                            self.assertEqual(
                            2, len(Session.categories),
                            f"Expected categories amount after backup load is 2 returned {len(Session.categories)}")

                            self.assertEqual(
                            2, len(Session.db.category_query.get_all_categories()),
                            f"Expected categories amount after backup load is 2 returned {len(Session.db.category_query.get_all_categories())}")

                            def _load_newest_backup() -> None:
                                """Load automatically created backup that has new income category"""

                                WindowsRegistry.BackupManagementWindow.backups_table.selectRow(0)

                                def _check_load_confirmation() -> None:
                                    """Check if load backup confirmation message is shown"""

                                    self.assertEqual(WindowsRegistry.Messages.load_backup_confirmation.isVisible(), True, "Load backup confirmation message hasn't been shown")
                                    WindowsRegistry.Messages.load_backup_confirmation.ok_button.click()
                                QTimer.singleShot(100, _check_load_confirmation)
                                WindowsRegistry.BackupManagementWindow.load_backup.click()

                                def _check_backup_load() -> None:
                                    """Check if backup is loaded and if new income category appears"""

                                    self.assertEqual(
                                    3, len(Session.categories),
                                    f"Expected categories amount after backup load is 3 returned {len(Session.categories)}")

                                    self.assertEqual(
                                    3, len(Session.db.category_query.get_all_categories()),
                                    f"Expected categories amount after backup load is 3 returned {len(Session.db.category_query.get_all_categories())}")

                                    self.assertEqual(WindowsRegistry.BackupManagementWindow.isVisible(), False, "Backup management window hasn't been closed")
                                    self.assertEqual(WindowsRegistry.SettingsWindow.isVisible(), False, "Settings window hasn't been closed")
                                QTimer.singleShot(200, _check_backup_load)

                            QTimer.singleShot(1000, partial(self.open_backup_management_window, _load_newest_backup))

                        QTimer.singleShot(1000, _check_backup_load)
                        WindowsRegistry.Messages.load_backup_confirmation.ok_button.click()

                    QTimer.singleShot(100, _check_load_confirmation)
                    WindowsRegistry.BackupManagementWindow.load_backup.click()

                QTimer.singleShot(200, partial(self.open_backup_management_window, _load_backup))
                WindowsRegistry.AddCategoryWindow.button.click()
            
            QTimer.singleShot(100, _add_category)
            WindowsRegistry.MainWindow.add_incomes_category.click()

        self.open_backup_management_window(_prepare_load_backup)
        qsleep(5000)
    

    def test_4_auto_backup_status_change(self) -> None:
        """Test changing auto backup status in the application."""

        def _set_daily_status() -> None:
            """Open auto backup window to set daily status"""

            def _choose_daily_auto_backup() -> None:
                """Set daily auto backup status and check if it is set correctly"""
                
                self.assertEqual(WindowsRegistry.AutoBackupWindow.isVisible(), True, "Auto backup window hasn't been opened")

                WindowsRegistry.AutoBackupWindow.daily.click()
                qsleep(100)

                self.assertEqual(WindowsRegistry.AutoBackupWindow.daily.isChecked(), True, "Daily auto backup hasn't been selected")
                self.assertEqual(WindowsRegistry.AutoBackupWindow.weekly.isChecked(), False, "Weekly auto backup hasn't been deselected")
                self.assertEqual(WindowsRegistry.AutoBackupWindow.monthly.isChecked(), False, "Monthly auto backup hasn't been deselected")

                WindowsRegistry.AutoBackupWindow.save.click()
                qsleep(200)

                self.assertEqual(WindowsRegistry.AutoBackupWindow.isVisible(), False, "Auto backup window hasn't been closed")
                self.assertEqual(Session.config.auto_backup_status, Session.config.AutoBackupStatus.DAILY.value, "Auto backup status hasn't been changed to daily")

                translated_daily_status = LanguageStructure.BackupManagement.get_translation(7)
                self.assertNotEqual(WindowsRegistry.AutoBackupWindow.current_status.text().find(translated_daily_status), -1, "Auto backup status label hasn't been changed to daily")
                self.assertNotEqual(WindowsRegistry.BackupManagementWindow.auto_backup_status.text().find(translated_daily_status), -1, "Auto backup status label hasn't been changed to daily")
                WindowsRegistry.BackupManagementWindow.done(0)
                WindowsRegistry.SettingsWindow.done(0)

            QTimer.singleShot(100, _choose_daily_auto_backup)
            WindowsRegistry.BackupManagementWindow.auto_backup.click()

        self.open_backup_management_window(_set_daily_status)
        qsleep(500)

        def _set_weekly_status() -> None:
            """Open auto backup window to set weekly status"""

            def _choose_weekly_auto_backup() -> None:
                """Set weekly auto backup status and check if it is set correctly"""

                self.assertEqual(WindowsRegistry.AutoBackupWindow.isVisible(), True, "Auto backup window hasn't been opened")

                WindowsRegistry.AutoBackupWindow.weekly.click()
                qsleep(100)

                self.assertEqual(WindowsRegistry.AutoBackupWindow.daily.isChecked(), False, "Daily auto backup hasn't been deselected")
                self.assertEqual(WindowsRegistry.AutoBackupWindow.weekly.isChecked(), True, "Weekly auto backup hasn't been selected")
                self.assertEqual(WindowsRegistry.AutoBackupWindow.monthly.isChecked(), False, "Monthly auto backup hasn't been deselected")

                WindowsRegistry.AutoBackupWindow.save.click()
                qsleep(200)

                self.assertEqual(WindowsRegistry.AutoBackupWindow.isVisible(), False, "Auto backup window hasn't been closed")
                self.assertEqual(Session.config.auto_backup_status, Session.config.AutoBackupStatus.WEEKLY.value, "Auto backup status hasn't been changed to weekly")

                translated_weekly_status = LanguageStructure.BackupManagement.get_translation(6)
                self.assertNotEqual(WindowsRegistry.AutoBackupWindow.current_status.text().find(translated_weekly_status), -1, "Auto backup status label hasn't been changed to weekly")
                self.assertNotEqual(WindowsRegistry.BackupManagementWindow.auto_backup_status.text().find(translated_weekly_status), -1, "Auto backup status label hasn't been changed to weekly")
                WindowsRegistry.BackupManagementWindow.done(0)
                WindowsRegistry.SettingsWindow.done(0)

            QTimer.singleShot(100, _choose_weekly_auto_backup)
            WindowsRegistry.BackupManagementWindow.auto_backup.click()

        self.open_backup_management_window(_set_weekly_status)
        qsleep(500)

        def _set_monthly_status() -> None:
            """Open auto backup window to set monthly status"""

            def _choose_monthly_auto_backup() -> None:
                """Set monthly auto backup status and check if it is set correctly"""

                self.assertEqual(WindowsRegistry.AutoBackupWindow.isVisible(), True, "Auto backup window hasn't been opened")

                WindowsRegistry.AutoBackupWindow.monthly.click()
                qsleep(100)

                self.assertEqual(WindowsRegistry.AutoBackupWindow.daily.isChecked(), False, "Daily auto backup hasn't been deselected")
                self.assertEqual(WindowsRegistry.AutoBackupWindow.weekly.isChecked(), False, "Weekly auto backup hasn't been deselected")
                self.assertEqual(WindowsRegistry.AutoBackupWindow.monthly.isChecked(), True, "Monthly auto backup hasn't been selected")

                WindowsRegistry.AutoBackupWindow.save.click()
                qsleep(200)

                self.assertEqual(WindowsRegistry.AutoBackupWindow.isVisible(), False, "Auto backup window hasn't been closed")
                self.assertEqual(Session.config.auto_backup_status, Session.config.AutoBackupStatus.MONTHLY.value, "Auto backup status hasn't been changed to monthly")

                translated_monthly_status = LanguageStructure.BackupManagement.get_translation(5)
                self.assertNotEqual(WindowsRegistry.AutoBackupWindow.current_status.text().find(translated_monthly_status), -1, "Auto backup status label hasn't been changed to monthly")
                self.assertNotEqual(WindowsRegistry.BackupManagementWindow.auto_backup_status.text().find(translated_monthly_status), -1, "Auto backup status label hasn't been changed to monthly")
                WindowsRegistry.BackupManagementWindow.done(0)
                WindowsRegistry.SettingsWindow.done(0)

            QTimer.singleShot(100, _choose_monthly_auto_backup)
            WindowsRegistry.BackupManagementWindow.auto_backup.click()

        self.open_backup_management_window(_set_monthly_status)
        qsleep(500)


    def test_5_auto_daily_backup(self) -> None:
        """Test daily auto backup in the application."""

        Session.config.auto_backup_status = Session.config.AutoBackupStatus.DAILY.value
        date_now = datetime.now()
        date_minus_1_day = date_now - timedelta(days=1)

        def _prepare_auto_daily_backup() -> None:
            """Create fresh backup with current date"""

            def _check_backup_appearance() -> None:
                """Check if backup is created and added to the table"""

                self.assertEqual(
                1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been added to the table or more then 1 backup is added {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}")

                self.assertEqual(
                1, len(Session.backups),
                f"Backup hasn't been added to the session or more then 1 backup is added {len(Session.backups)}")

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more then 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                def _check_no_new_backup() -> None:
                    """Check if no new backup is created since last backup is new"""

                    self.assertEqual(
                    1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                    f"Backup have been added even though less then 1 day has passed {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    1, len(Session.backups),
                    f"Backup have been added even though less then 1 day has passed {len(Session.backups)}")

                    self.assertEqual(
                    1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file have been created even though less then 1 day has passed {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                QTimer.singleShot(200, _check_no_new_backup)
                auto_backup()
                qsleep(500)
                
                backup = Session.backups[WindowsRegistry.BackupManagementWindow.backups_table.item(0, 2).text()]
                backup.timestamp = date_minus_1_day.strftime(BACKUPS_DATE_FORMAT)

                def _check_second_backup_appearance() -> None:
                    """After mocking backup timestamp check if second backup is created"""

                    self.assertEqual(
                    2, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                    f"Backup during daily auto backup hasn't been added to the table or more then 2 backups are added {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    2, len(Session.backups),
                    f"Backup during daily auto backup hasn't been added to the session or more then 2 backups are added {len(Session.backups)}")

                    self.assertEqual(
                    2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file during daily auto backup hasn't been created or more then 2 backups are created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                    WindowsRegistry.BackupManagementWindow.done(0)
                    WindowsRegistry.SettingsWindow.done(0)

                QTimer.singleShot(1000, _check_second_backup_appearance)
                auto_backup()
                
            qsleep(1000)
            QTimer.singleShot(1000, _check_backup_appearance)
            WindowsRegistry.BackupManagementWindow.create_backup.click()
        
        QTimer.singleShot(200, _prepare_auto_daily_backup)
        qsleep(5000)


    def test_6_auto_weekly_backup(self) -> None:
        """Test weekly auto backup in the application."""

        Session.config.auto_backup_status = Session.config.AutoBackupStatus.WEEKLY.value
        date_now = datetime.now()
        date_minus_7_days = date_now - timedelta(days=7)

        def _prepare_auto_weekly_backup() -> None:
            """Create fresh backup with current date"""

            def _check_backup_appearance() -> None:
                """Check if backup is created and added to the table"""

                self.assertEqual(
                1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been added to the table or more then 1 backup is added {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}")

                self.assertEqual(
                1, len(Session.backups),
                f"Backup hasn't been added to the session or more then 1 backup is added {len(Session.backups)}")

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more then 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                def _check_no_new_backup() -> None:
                    """Check if no new backup is created since last backup is new"""

                    self.assertEqual(
                    1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                    f"Backup have been added even though less then 7 days has passed {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    1, len(Session.backups),
                    f"Backup have been added even though less then 7 days has passed {len(Session.backups)}")

                    self.assertEqual(
                    1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file have been created even though less then 7 days has passed {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                QTimer.singleShot(200, _check_no_new_backup)
                auto_backup()
                qsleep(500)
                
                backup = Session.backups[WindowsRegistry.BackupManagementWindow.backups_table.item(0, 2).text()]
                backup.timestamp = date_minus_7_days.strftime(BACKUPS_DATE_FORMAT)

                def _check_second_backup_appearance() -> None:
                    """After mocking backup timestamp check if second backup is created"""

                    self.assertEqual(
                    2, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                    f"Backup during weekly auto backup hasn't been added to the table or more then 2 backups are added {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    2, len(Session.backups),
                    f"Backup during weekly auto backup hasn't been added to the session or more then 2 backups are added {len(Session.backups)}")

                    self.assertEqual(
                    2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file during weekly auto backup hasn't been created or more then 2 backups are created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                    WindowsRegistry.BackupManagementWindow.done(0)
                    WindowsRegistry.SettingsWindow.done(0)

                QTimer.singleShot(1000, _check_second_backup_appearance)
                auto_backup()

            QTimer.singleShot(1200, _check_backup_appearance)
            WindowsRegistry.BackupManagementWindow.create_backup.click()

        QTimer.singleShot(100, _prepare_auto_weekly_backup)
        qsleep(5000)
    

    def test_7_auto_monthly_backup(self) -> None:
        """Test monthly auto backup in the application."""

        Session.config.auto_backup_status = Session.config.AutoBackupStatus.MONTHLY.value
        date_now = datetime.now()
        date_minus_30_days = date_now - timedelta(days=30)

        def _prepare_auto_monthly_backup() -> None:
            """Create fresh backup with current date"""

            def _check_backup_appearance() -> None:
                """Check if backup is created and added to the table"""

                self.assertEqual(
                1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                f"Backup hasn't been added to the table or more then 1 backup is added {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}")

                self.assertEqual(
                1, len(Session.backups),
                f"Backup hasn't been added to the session or more then 1 backup is added {len(Session.backups)}")

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more then 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                def _check_no_new_backup() -> None:
                    """Check if no new backup is created since last backup is new"""

                    self.assertEqual(
                    1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                    f"Backup have been added even though less then 30 days has passed {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    1, len(Session.backups),
                    f"Backup have been added even though less then 30 days has passed {len(Session.backups)}")

                    self.assertEqual(
                    1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file have been created even though less then 30 days has passed {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                QTimer.singleShot(200, _check_no_new_backup)
                auto_backup()
                qsleep(500)
                
                backup = Session.backups[WindowsRegistry.BackupManagementWindow.backups_table.item(0, 2).text()]
                backup.timestamp = date_minus_30_days.strftime(BACKUPS_DATE_FORMAT)

                def _check_second_backup_appearance() -> None:
                    """After mocking backup timestamp check if second backup is created"""

                    self.assertEqual(
                    2, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                    f"Backup during monthly auto backup hasn't been added to the table or more then 2 backups are added {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}")

                    self.assertEqual(
                    2, len(Session.backups),
                    f"Backup during monthly auto backup hasn't been added to the session or more then 2 backups are added {len(Session.backups)}")

                    self.assertEqual(
                    2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file during monthly auto backup hasn't been created or more than 2 backups are created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                    WindowsRegistry.BackupManagementWindow.done(0)
                    WindowsRegistry.SettingsWindow.done(0)

                QTimer.singleShot(1000, _check_second_backup_appearance)
                auto_backup()

            QTimer.singleShot(1000, _check_backup_appearance)
            WindowsRegistry.BackupManagementWindow.create_backup.click()

        QTimer.singleShot(100, _prepare_auto_monthly_backup)
        qsleep(5000)


    def test_8_check_max_backups_change(self) -> None:
        """Test changing max backups amount in the application."""

        init_max_backups = Session.config.max_backups

        def _open_auto_backup_settings() -> None:
            """Open auto backup window to set new max backups amount"""

            def _set_new_max_backups() -> None:
                """Set new max backups amount and check if it is set correctly"""

                def _check_no_change() -> None:
                    """Check if no change is made to max backups amount after clicking save without changing anything"""

                    self.assertEqual(
                    init_max_backups, Session.config.max_backups,
                    f"Expected max backups amount in session is {init_max_backups} returned {Session.config.max_backups}")

                    Session.config.load_user_config()
                    self.assertEqual(
                    init_max_backups, Session.config.max_backups,
                    f"Expected max backups amount in user config is {init_max_backups} returned {Session.config.max_backups}")

                    self.assertNotEqual(
                    -1, WindowsRegistry.AutoBackupWindow.max_backups_label.text().find(str(init_max_backups)),
                    f"Expected max backups amount in label is {init_max_backups} returned {WindowsRegistry.AutoBackupWindow.max_backups_label.text()}")

                QTimer.singleShot(100, _check_no_change)
                WindowsRegistry.AutoBackupWindow.save.click()

                def _check_below_min_backups() -> None:
                    """Check if below min backups message is shown"""

                    self.assertEqual(WindowsRegistry.Messages.below_recommended_min_backups.isVisible(), True, "Below min backups message hasn't been shown")
                    WindowsRegistry.Messages.below_recommended_min_backups.ok_button.click()
                
                if MIN_RECOMMENDED_BACKUPS > 1:
                    QTimer.singleShot(200, _check_below_min_backups)
                    WindowsRegistry.AutoBackupWindow.max_backups.setText(str(MIN_RECOMMENDED_BACKUPS - 1))
                    WindowsRegistry.AutoBackupWindow.save.click()
                    qsleep(500)
                
                def _check_above_max_backups() -> None:
                    """Check if above max backups message is shown"""

                    self.assertEqual(WindowsRegistry.Messages.above_recommended_max_backups.isVisible(), True, "Above max backups message hasn't been shown")
                    WindowsRegistry.Messages.above_recommended_max_backups.ok_button.click()
                
                QTimer.singleShot(200, _check_above_max_backups)
                WindowsRegistry.AutoBackupWindow.max_backups.setText(str(MAX_RECOMMENDED_BACKUPS + 1))
                WindowsRegistry.AutoBackupWindow.save.click()
                qsleep(500)

                def _check_max_backups_change() -> None:
                    """Check if max backups amount is changed correctly"""

                    self.assertEqual(
                    3, Session.config.max_backups,
                    f"Expected max backups amount in session is 3 returned {Session.config.max_backups}")

                    Session.config.load_user_config()
                    self.assertEqual(
                    3, Session.config.max_backups,
                    f"Expected max backups amount in user config is 3 returned {Session.config.max_backups}")
                    
                    self.assertNotEqual(
                    -1, WindowsRegistry.AutoBackupWindow.max_backups_label.text().find("3"),
                    f"Expected max backups amount in label is 3 returned {WindowsRegistry.AutoBackupWindow.max_backups_label.text()}")

                    WindowsRegistry.AutoBackupWindow.done(0)
                    WindowsRegistry.BackupManagementWindow.done(0)
                    WindowsRegistry.SettingsWindow.done(0)

                QTimer.singleShot(200, _check_max_backups_change)
                WindowsRegistry.AutoBackupWindow.max_backups.setText("3")
                WindowsRegistry.AutoBackupWindow.save.click()

            QTimer.singleShot(100, _set_new_max_backups)
            WindowsRegistry.BackupManagementWindow.auto_backup.click()
            
        self.open_backup_management_window(_open_auto_backup_settings)
        qsleep(1000)

                    


            
