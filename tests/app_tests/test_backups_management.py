from __future__ import annotations
from typing import TYPE_CHECKING
import os
from functools import partial
from datetime import datetime, timedelta
from PySide6.QtCore import QTimer

from languages import LanguageStructure
from project_configuration import TEST_BACKUPS_DIRECTORY, MIN_RECOMMENDED_BACKUPS, MAX_RECOMMENDED_BACKUPS,\
    BACKUPS_DATE_FORMAT
from tests.tests_toolkit import DBTestCase, OutOfScopeTestCase, qsleep
from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry
from DesktopQtToolkit.Utils import get_table_widget_item

from AppManagement.backup_management import auto_backup

if TYPE_CHECKING:
    from typing import Callable



class TestBackupsManagement(DBTestCase, OutOfScopeTestCase):
    """Test backup management in the application."""

    TIMEOUT_SEC = 20

    def open_backup_management_window(self, func:Callable[[], None]) -> None:
        """Open backup management window and call function after some delay.

            Arguments
            ---------
                `func` : (function) - Function to call after opening backup management window.
        """

        def _open_backup_management() -> None:
            QTimer.singleShot(100, self.catch_failure(func))
            self.click_on_widget(WindowsRegistry.SettingsWindow.backup_management)

        QTimer.singleShot(100, self.catch_failure(_open_backup_management))
        self.click_on_widget(WindowsRegistry.MainWindow.settings)
    

    def open_auto_backup_window(self, func:Callable[[], None]) -> None:
        """Open auto backup window and call function after some delay.

            Arguments
            ---------
                `func` : (function) - Function to call after opening auto backup window.
        """

        def _open_auto_backup() -> None:
            QTimer.singleShot(100, self.catch_failure(func))
            self.click_on_widget(WindowsRegistry.SettingsWindow.auto_backup)
            WindowsRegistry.AutoBackupWindow.done(1)
            WindowsRegistry.SettingsWindow.done(1)

        QTimer.singleShot(100, self.catch_failure(_open_auto_backup))

        self.click_on_widget(WindowsRegistry.MainWindow.settings)


    def test_1_create_backup(self) -> None:
        """Test creating backup in the application."""

        app_core = AppCore.instance()
        def _create_backup() -> None:
            """Click create backup button"""

            self.click_on_widget(WindowsRegistry.BackupManagementWindow.create_backup)

            def _check_backup_appearance() -> None:
                """Check if backup is created and added to the table"""

                self.assertEqual(
                1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                    f"Backup hasn't been added to the table or more than 1 backup is added\
                    {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}"
                )

                self.assertEqual(
                1, len(app_core.backups),
                f"Backup hasn't been added to the session or more than 1 backup is added {len(app_core.backups)}")

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file hasn't been created or more than 1 backup is created\
                    {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                )

                self.assertEqual(
                    WindowsRegistry.BackupManagementWindow.create_backup.isEnabled(),
                    True,
                    "Create backup button hasn't been enabled"
                )
                
                WindowsRegistry.BackupManagementWindow.done(0)
                WindowsRegistry.SettingsWindow.done(0)

            self.assertEqual(
                WindowsRegistry.BackupManagementWindow.create_backup.isEnabled(),
                False,
                "Create backup button hasn't been disabled"
            )
            QTimer.singleShot(1200, self.catch_failure(_check_backup_appearance))

        self.open_backup_management_window(_create_backup)

        qsleep(2000)
    

    def test_2_remove_backup(self) -> None:
        """Test removing backup in the application."""

        app_core = AppCore.instance()
        def _remove_backup() -> None:
            """Create example backup and remove it"""

            self.click_on_widget(WindowsRegistry.BackupManagementWindow.create_backup)

            def _check_no_selection() -> None:
                """Check if no backup is selected"""
                
                self.assertEqual(
                    WindowsRegistry.Messages.unselected_row.isVisible(),
                    True,
                    "Unselected row message hasn't been shown"
                )
                self.click_on_widget(WindowsRegistry.Messages.unselected_row.ok_button)
            QTimer.singleShot(100, self.catch_failure(_check_no_selection))
            self.click_on_widget(WindowsRegistry.BackupManagementWindow.delete_backup)

            qsleep(5000)

            WindowsRegistry.BackupManagementWindow.backups_table.selectRow(0)
            def _check_below_min_backups() -> None:
                """Check if below min backups message is shown"""

                self.assertEqual(
                    WindowsRegistry.Messages.below_recommended_min_backups.isVisible(),
                    True,
                    "Below min backups message hasn't been shown"
                )
                self.click_on_widget(WindowsRegistry.Messages.below_recommended_min_backups.ok_button)
            QTimer.singleShot(200, self.catch_failure(_check_below_min_backups))
            self.click_on_widget(WindowsRegistry.BackupManagementWindow.delete_backup)

            def _check_backup_deletion() -> None:
                """Check if backup is deleted from the table and session"""

                self.assertEqual(
                    0, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                    f"Backup hasn't been removed from the table or more than 0 backups are left\
                    {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}"
                )

                self.assertEqual(
                    0, len(app_core.backups),
                    f"Backup hasn't been removed from the session or more than 0 backups are left {len(app_core.backups)}"
                )

                self.assertEqual(
                    0, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file hasn't been removed or more than 0 backups are left {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                )

                WindowsRegistry.BackupManagementWindow.done(0)
                WindowsRegistry.SettingsWindow.done(0)
            
            QTimer.singleShot(500, self.catch_failure(_check_backup_deletion))
    
        self.open_backup_management_window(_remove_backup)

        qsleep(3000)
        

    def test_3_load_backup(self) -> None:
        """Test loading backup in the application."""

        app_core = AppCore.instance()
        WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(0)
        def _prepare_load_backup() -> None:
            """Create new backup that doesn't have new income category and load it"""

            self.click_on_widget(WindowsRegistry.BackupManagementWindow.create_backup)
            WindowsRegistry.BackupManagementWindow.done(0)
            WindowsRegistry.SettingsWindow.done(0)

            def _add_category() -> None:
                """Add new income category to the session"""

                WindowsRegistry.AddCategoryWindow.category_name.setText("Test backup category name")
                def _load_backup() -> None:
                    """Load backup that doesn't have new income category"""

                    def _check_no_selection() -> None:
                        """Check if no backup is selected"""

                        self.assertEqual(
                            WindowsRegistry.Messages.unselected_row.isVisible(),
                            True,
                            "Unselected row message hasn't been shown"
                        )
                        self.click_on_widget(WindowsRegistry.Messages.unselected_row.ok_button)
                    QTimer.singleShot(100, self.catch_failure(_check_no_selection))
                    self.click_on_widget(WindowsRegistry.BackupManagementWindow.load_backup)

                    qsleep(1000)

                    WindowsRegistry.BackupManagementWindow.backups_table.selectRow(0)

                    def _check_load_confirmation() -> None:
                        """Check if load backup confirmation message is shown"""

                        self.assertEqual(
                            WindowsRegistry.Messages.load_backup_confirmation.isVisible(),
                            True,
                            "Load backup confirmation message hasn't been shown"
                        )

                        def _check_backup_load() -> None:
                            """Check if backup is loaded and if new income category doesn't appears"""

                            self.assertEqual(
                            2, len(app_core.categories),
                            f"Expected categories amount after backup load is 2 returned {len(app_core.categories)}")

                            self.assertEqual(
                                2, len(app_core.db.category_query.get_all_categories()),
                                f"Expected categories amount after backup load is 2 returned\
                                {len(app_core.db.category_query.get_all_categories())}"
                            )

                            def _load_newest_backup() -> None:
                                """Load automatically created backup that has new income category"""

                                WindowsRegistry.BackupManagementWindow.backups_table.selectRow(0)

                                def _check_load_confirmation() -> None:
                                    """Check if load backup confirmation message is shown"""

                                    self.assertEqual(
                                        WindowsRegistry.Messages.load_backup_confirmation.isVisible(),
                                        True,
                                        "Load backup confirmation message hasn't been shown"
                                    )
                                    self.click_on_widget(WindowsRegistry.Messages.load_backup_confirmation.ok_button)
                                QTimer.singleShot(100, self.catch_failure(_check_load_confirmation))
                                self.click_on_widget(WindowsRegistry.BackupManagementWindow.load_backup)

                                def _check_backup_load() -> None:
                                    """Check if backup is loaded and if new income category appears"""

                                    self.assertEqual(
                                    3, len(app_core.categories),
                                    f"Expected categories amount after backup load is 3 returned {len(app_core.categories)}")

                                    self.assertEqual(
                                        3, len(app_core.db.category_query.get_all_categories()),
                                        f"Expected categories amount after backup load is 3 returned \
                                        {len(app_core.db.category_query.get_all_categories())}"
                                    )

                                    self.assertEqual(
                                        WindowsRegistry.BackupManagementWindow.isVisible(),
                                        False,
                                        "Backup management window hasn't been closed"
                                    )
                                    self.assertEqual(
                                        WindowsRegistry.SettingsWindow.isVisible(),
                                        False,
                                        "Settings window hasn't been closed"
                                    )
                                QTimer.singleShot(200, self.catch_failure(_check_backup_load))

                            QTimer.singleShot(1000, partial(
                                self.open_backup_management_window,
                                self.catch_failure(_load_newest_backup)
                            ))

                        QTimer.singleShot(1000, self.catch_failure(_check_backup_load))
                        self.click_on_widget(WindowsRegistry.Messages.load_backup_confirmation.ok_button)

                    QTimer.singleShot(100, self.catch_failure(_check_load_confirmation))
                    self.click_on_widget(WindowsRegistry.BackupManagementWindow.load_backup)

                qsleep(1000)
                QTimer.singleShot(200, partial(self.open_backup_management_window, self.catch_failure(_load_backup)))
                self.click_on_widget(WindowsRegistry.AddCategoryWindow.button)

            qsleep(1000)
            QTimer.singleShot(100, self.catch_failure(_add_category))
            self.click_on_widget(WindowsRegistry.MainWindow.add_incomes_category)

        self.open_backup_management_window(_prepare_load_backup)
        qsleep(7000)
    

    def test_4_auto_backup_status_change(self) -> None:
        """Test changing auto backup status in the application."""

        app_core = AppCore.instance()
        def _set_daily_status() -> None:
            """Open auto backup window to set daily status"""

            def _choose_daily_auto_backup() -> None:
                """Set daily auto backup status and check if it is set correctly"""
                
                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.isVisible(),
                    True,
                    "Auto backup window hasn't been opened"
                )

                self.click_on_widget(WindowsRegistry.AutoBackupWindow.daily)
                qsleep(100)

                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.daily.isChecked(),
                    True,
                    "Daily auto backup hasn't been selected"
                )
                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.weekly.isChecked(),
                    False,
                    "Weekly auto backup hasn't been deselected"
                )
                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.monthly.isChecked(),
                    False,
                    "Monthly auto backup hasn't been deselected"
                )

                self.click_on_widget(WindowsRegistry.AutoBackupWindow.save)
                qsleep(200)

                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.isVisible(),
                    False,
                    "Auto backup window hasn't been closed"
                )
                self.assertEqual(
                    app_core.config.auto_backup_status,
                    app_core.config.AutoBackupStatus.DAILY.value,
                    "Auto backup status hasn't been changed to daily"
                )

                translated_daily_status = LanguageStructure.BackupManagement.get_translation(7)
                self.assertNotEqual(
                    WindowsRegistry.AutoBackupWindow.current_status.text().find(translated_daily_status),
                    -1,
                    "Auto backup status label hasn't been changed to daily"
                )
                self.assertNotEqual(
                    WindowsRegistry.SettingsWindow.auto_backup_status.text().find(translated_daily_status),
                    -1,
                    "Auto backup status label hasn't been changed to daily"
                )
                WindowsRegistry.BackupManagementWindow.done(0)
                WindowsRegistry.SettingsWindow.done(0)

            QTimer.singleShot(100, self.catch_failure(_choose_daily_auto_backup))
            self.click_on_widget(WindowsRegistry.SettingsWindow.auto_backup)

        self.open_backup_management_window(_set_daily_status)
        qsleep(500)

        def _set_weekly_status() -> None:
            """Open auto backup window to set weekly status"""

            def _choose_weekly_auto_backup() -> None:
                """Set weekly auto backup status and check if it is set correctly"""

                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.isVisible(),
                    True,
                    "Auto backup window hasn't been opened"
                )

                self.click_on_widget(WindowsRegistry.AutoBackupWindow.weekly)
                qsleep(100)

                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.daily.isChecked(),
                    False,
                    "Daily auto backup hasn't been deselected"
                )
                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.weekly.isChecked(),
                    True,
                    "Weekly auto backup hasn't been selected"
                )
                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.monthly.isChecked(),
                    False,
                    "Monthly auto backup hasn't been deselected"
                )

                self.click_on_widget(WindowsRegistry.AutoBackupWindow.save)
                qsleep(200)

                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.isVisible(),
                    False,
                    "Auto backup window hasn't been closed"
                )
                self.assertEqual(
                    app_core.config.auto_backup_status,
                    app_core.config.AutoBackupStatus.WEEKLY.value,
                    "Auto backup status hasn't been changed to weekly"
                )

                translated_weekly_status = LanguageStructure.BackupManagement.get_translation(6)
                self.assertNotEqual(
                    WindowsRegistry.AutoBackupWindow.current_status.text().find(translated_weekly_status),
                    -1,
                    "Auto backup status label hasn't been changed to weekly"
                )
                self.assertNotEqual(
                    WindowsRegistry.SettingsWindow.auto_backup_status.text().find(translated_weekly_status),
                    -1,
                    "Auto backup status label hasn't been changed to weekly"
                )
                WindowsRegistry.BackupManagementWindow.done(0)
                WindowsRegistry.SettingsWindow.done(0)

            QTimer.singleShot(100, self.catch_failure(_choose_weekly_auto_backup))
            self.click_on_widget(WindowsRegistry.SettingsWindow.auto_backup)

        self.open_backup_management_window(_set_weekly_status)
        qsleep(500)

        def _set_monthly_status() -> None:
            """Open auto backup window to set monthly status"""

            def _choose_monthly_auto_backup() -> None:
                """Set monthly auto backup status and check if it is set correctly"""

                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.isVisible(), True, "Auto backup window hasn't been opened"
                )

                self.click_on_widget(WindowsRegistry.AutoBackupWindow.monthly)
                qsleep(100)

                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.daily.isChecked(), False, "Daily auto backup hasn't been deselected"
                )
                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.weekly.isChecked(), False, "Weekly auto backup hasn't been deselected"
                )
                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.monthly.isChecked(), True, "Monthly auto backup hasn't been selected"
                )

                self.click_on_widget(WindowsRegistry.AutoBackupWindow.save)
                qsleep(200)

                self.assertEqual(
                    WindowsRegistry.AutoBackupWindow.isVisible(),
                    False,
                    "Auto backup window hasn't been closed"
                )
                self.assertEqual(
                    app_core.config.auto_backup_status,
                    app_core.config.AutoBackupStatus.MONTHLY.value,
                    "Auto backup status hasn't been changed to monthly"
                )

                translated_monthly_status = LanguageStructure.BackupManagement.get_translation(5)
                self.assertNotEqual(
                    WindowsRegistry.AutoBackupWindow.current_status.text().find(translated_monthly_status),
                    -1,
                    "Auto backup status label hasn't been changed to monthly"
                )
                self.assertNotEqual(
                    WindowsRegistry.SettingsWindow.auto_backup_status.text().find(translated_monthly_status),
                    -1,
                    "Auto backup status label hasn't been changed to monthly"
                )
                WindowsRegistry.BackupManagementWindow.done(0)
                WindowsRegistry.SettingsWindow.done(0)

            QTimer.singleShot(100, self.catch_failure(_choose_monthly_auto_backup))
            self.click_on_widget(WindowsRegistry.SettingsWindow.auto_backup)

        self.open_backup_management_window(_set_monthly_status)
        qsleep(500)


    def test_5_auto_daily_backup(self) -> None:
        """Test daily auto backup in the application."""

        app_core = AppCore.instance()
        app_core.config.auto_backup_status = app_core.config.AutoBackupStatus.DAILY.value
        date_now = datetime.now()
        date_minus_1_day = date_now - timedelta(days=1)

        def _prepare_auto_daily_backup() -> None:
            """Create fresh backup with current date"""

            def _check_backup_appearance() -> None:
                """Check if backup is created and added to the table"""

                self.assertEqual(
                    1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                    f"Backup hasn't been added to the table or more than 1 backup is added \
                    {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}"
                )

                self.assertEqual(
                1, len(app_core.backups),
                f"Backup hasn't been added to the session or more than 1 backup is added {len(app_core.backups)}")

                self.assertEqual(
                    1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file hasn't been created or more than 1 backup is created \
                    {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                )

                def _check_no_new_backup() -> None:
                    """Check if no new backup is created since last backup is new"""

                    self.assertEqual(
                        1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                        f"Backup have been added even though less than 1 day has passed \
                        {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                    1, len(app_core.backups),
                    f"Backup have been added even though less than 1 day has passed {len(app_core.backups)}")

                    self.assertEqual(
                        1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                        f"Backup file have been created even though less than 1 day has passed \
                        {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                QTimer.singleShot(200, self.catch_failure(_check_no_new_backup))
                auto_backup()
                qsleep(500)
                
                backup = app_core.backups[get_table_widget_item(WindowsRegistry.BackupManagementWindow.backups_table, 0, 2).text()]
                backup.timestamp = date_minus_1_day.strftime(BACKUPS_DATE_FORMAT)

                def _check_second_backup_appearance() -> None:
                    """After mocking backup timestamp check if second backup is created"""

                    self.assertEqual(
                        2, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                        f"Backup during daily auto backup hasn't been added to the table or more than 2 backups are added \
                        {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                        2, len(app_core.backups),
                        f"Backup during daily auto backup hasn't been added to the session or more than 2 backups are added \
                        {len(app_core.backups)}"
                    )

                    self.assertEqual(
                        2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                        f"Backup file during daily auto backup hasn't been created or more than 2 backups are created \
                        {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                    WindowsRegistry.BackupManagementWindow.done(0)
                    WindowsRegistry.SettingsWindow.done(0)

                QTimer.singleShot(1000, self.catch_failure(_check_second_backup_appearance))
                auto_backup()
                
            qsleep(1000)
            QTimer.singleShot(1500, self.catch_failure(_check_backup_appearance))
            self.click_on_widget(WindowsRegistry.BackupManagementWindow.create_backup)
        
        self.open_backup_management_window(_prepare_auto_daily_backup)
        qsleep(6000)


    def test_6_auto_weekly_backup(self) -> None:
        """Test weekly auto backup in the application."""

        app_core = AppCore.instance()
        app_core.config.auto_backup_status = app_core.config.AutoBackupStatus.WEEKLY.value
        date_now = datetime.now()
        date_minus_7_days = date_now - timedelta(days=7)

        def _prepare_auto_weekly_backup() -> None:
            """Create fresh backup with current date"""

            def _check_backup_appearance() -> None:
                """Check if backup is created and added to the table"""

                self.assertEqual(
                    1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                    f"Backup hasn't been added to the table or more than 1 backup is added \
                    {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}"
                )

                self.assertEqual(
                1, len(app_core.backups),
                f"Backup hasn't been added to the session or more than 1 backup is added {len(app_core.backups)}")

                self.assertEqual(
                    1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                    f"Backup file hasn't been created or more than 1 backup is created \
                    {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                )

                def _check_no_new_backup() -> None:
                    """Check if no new backup is created since last backup is new"""

                    self.assertEqual(
                        1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                        f"Backup have been added even though less than 7 days has passed \
                        {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                    1, len(app_core.backups),
                    f"Backup have been added even though less than 7 days has passed {len(app_core.backups)}")

                    self.assertEqual(
                        1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                        f"Backup file have been created even though less than 7 days has passed \
                        {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                QTimer.singleShot(200, self.catch_failure(_check_no_new_backup))
                auto_backup()
                qsleep(500)
                
                backup = app_core.backups[get_table_widget_item(WindowsRegistry.BackupManagementWindow.backups_table, 0, 2).text()]
                backup.timestamp = date_minus_7_days.strftime(BACKUPS_DATE_FORMAT)

                def _check_second_backup_appearance() -> None:
                    """After mocking backup timestamp check if second backup is created"""

                    self.assertEqual(
                        2, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                        f"Backup during weekly auto backup hasn't been added to the table or more than 2 backups are added \
                        {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                        2, len(app_core.backups),
                        f"Backup during weekly auto backup hasn't been added to the session or more than 2 backups are added \
                        {len(app_core.backups)}"
                    )

                    self.assertEqual(
                        2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                        f"Backup file during weekly auto backup hasn't been created or more than 2 backups are created \
                        {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                    WindowsRegistry.BackupManagementWindow.done(0)
                    WindowsRegistry.SettingsWindow.done(0)

                QTimer.singleShot(1000, self.catch_failure(_check_second_backup_appearance))
                auto_backup()

            QTimer.singleShot(1500, self.catch_failure(_check_backup_appearance))
            self.click_on_widget(WindowsRegistry.BackupManagementWindow.create_backup)

        self.open_backup_management_window(_prepare_auto_weekly_backup)
        qsleep(6000)
    

    def test_7_auto_monthly_backup(self) -> None:
        """Test monthly auto backup in the application."""

        app_core = AppCore.instance()
        app_core.config.auto_backup_status = app_core.config.AutoBackupStatus.MONTHLY.value
        date_now = datetime.now()
        date_minus_31_days = date_now - timedelta(days=31)

        def _prepare_auto_monthly_backup() -> None:
            """Create fresh backup with current date"""

            def _check_backup_appearance() -> None:
                """Check if backup is created and added to the table"""

                self.assertEqual(
                    1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                    f"Backup hasn't been added to the table or more than 1 backup is added \
                    {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}"
                )

                self.assertEqual(
                1, len(app_core.backups),
                f"Backup hasn't been added to the session or more than 1 backup is added {len(app_core.backups)}")

                self.assertEqual(
                1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                f"Backup file hasn't been created or more than 1 backup is created {len(os.listdir(TEST_BACKUPS_DIRECTORY))}")

                def _check_no_new_backup() -> None:
                    """Check if no new backup is created since last backup is new"""

                    self.assertEqual(
                        1, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                        f"Backup have been added even though less than 30 days has passed \
                        {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                    1, len(app_core.backups),
                    f"Backup have been added even though less than 30 days has passed {len(app_core.backups)}")

                    self.assertEqual(
                        1, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                        f"Backup file have been created even though less than 30 days has passed \
                        {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                QTimer.singleShot(200, self.catch_failure(_check_no_new_backup))
                auto_backup()
                qsleep(500)
                
                backup = app_core.backups[get_table_widget_item(WindowsRegistry.BackupManagementWindow.backups_table, 0, 2).text()]
                backup.timestamp = date_minus_31_days.strftime(BACKUPS_DATE_FORMAT)

                def _check_second_backup_appearance() -> None:
                    """After mocking backup timestamp check if second backup is created"""

                    self.assertEqual(
                        2, WindowsRegistry.BackupManagementWindow.backups_table.rowCount(),
                        f"Backup during monthly auto backup hasn't been added to the table or more than 2 backups are added \
                        {WindowsRegistry.BackupManagementWindow.backups_table.rowCount()}"
                    )

                    self.assertEqual(
                        2, len(app_core.backups),
                        f"Backup during monthly auto backup hasn't been added to the session or more than 2 backups are added \
                        {len(app_core.backups)}"
                    )

                    self.assertEqual(
                        2, len(os.listdir(TEST_BACKUPS_DIRECTORY)),
                        f"Backup file during monthly auto backup hasn't been created or more than 2 backups are created \
                        {len(os.listdir(TEST_BACKUPS_DIRECTORY))}"
                    )

                    WindowsRegistry.BackupManagementWindow.done(0)
                    WindowsRegistry.SettingsWindow.done(0)

                QTimer.singleShot(1000, self.catch_failure(_check_second_backup_appearance))
                auto_backup()

            QTimer.singleShot(1500, self.catch_failure(_check_backup_appearance))
            self.click_on_widget(WindowsRegistry.BackupManagementWindow.create_backup)

        self.open_backup_management_window(_prepare_auto_monthly_backup)
        qsleep(6000)


    def test_8_check_max_backups_change(self) -> None:
        """Test changing max backups amount in the application."""

        app_core = AppCore.instance()
        init_max_backups = app_core.config.max_backups
        new_max_backups = MIN_RECOMMENDED_BACKUPS + 1

        def _check_no_change() -> None:
            """Check if no change is made to max backups amount after clicking save without changing anything"""

            self.click_on_widget(WindowsRegistry.AutoBackupWindow.save)
            qsleep(100)

            self.assertEqual(
            init_max_backups, app_core.config.max_backups,
            f"Expected max backups amount in session is {init_max_backups} returned {app_core.config.max_backups}")

            app_core.config.load_user_config()
            self.assertEqual(
            init_max_backups, app_core.config.max_backups,
            f"Expected max backups amount in user config is {init_max_backups} returned {app_core.config.max_backups}")

            self.assertNotEqual(
                -1, WindowsRegistry.AutoBackupWindow.max_backups_label.text().find(str(init_max_backups)),
                f"Expected max backups amount in label is {init_max_backups} returned \
                {WindowsRegistry.AutoBackupWindow.max_backups_label.text()}"
            )

        self.open_auto_backup_window(_check_no_change)

        def _try_to_go_below_min_backups() -> None:
            """Try to set max backups amount below min and check if message is shown"""

            def _check_below_min_backups() -> None:
                """Check if below min backups message is shown"""

                self.assertEqual(
                    WindowsRegistry.Messages.below_recommended_min_backups.isVisible(),
                    True,
                    "Below min backups message hasn't been shown"
                )
                self.click_on_widget(WindowsRegistry.Messages.below_recommended_min_backups.ok_button)

            QTimer.singleShot(200, self.catch_failure(_check_below_min_backups))
            WindowsRegistry.AutoBackupWindow.max_backups.setText(str(MIN_RECOMMENDED_BACKUPS - 1))
            self.click_on_widget(WindowsRegistry.AutoBackupWindow.save)

        if MIN_RECOMMENDED_BACKUPS > 1:
            self.open_auto_backup_window(_try_to_go_below_min_backups)

        def _try_to_go_above_max_backups() -> None:
            """Try to set max backups amount above max and check if message is shown"""

            def _check_above_max_backups() -> None:
                """Check if above max backups message is shown"""

                self.assertEqual(
                    WindowsRegistry.Messages.above_recommended_max_backups.isVisible(),
                    True,
                    "Above max backups message hasn't been shown"
                )
                self.click_on_widget(WindowsRegistry.Messages.above_recommended_max_backups.ok_button)
        
            QTimer.singleShot(200, self.catch_failure(_check_above_max_backups))
            WindowsRegistry.AutoBackupWindow.max_backups.setText(str(MAX_RECOMMENDED_BACKUPS + 1))
            self.click_on_widget(WindowsRegistry.AutoBackupWindow.save)

        self.open_auto_backup_window(_try_to_go_above_max_backups)

        def _try_to_change_max_backups() -> None:
            """Try to change max backups amount"""

            def _check_max_backups_change() -> None:
                """Check if max backups amount is changed correctly"""

                self.assertEqual(
                new_max_backups, app_core.config.max_backups,
                f"Expected max backups amount in session is {new_max_backups} returned {app_core.config.max_backups}")

                app_core.config.load_user_config()
                self.assertEqual(
                new_max_backups, app_core.config.max_backups,
                f"Expected max backups amount in user config is {new_max_backups} returned {app_core.config.max_backups}")
                
                self.assertNotEqual(
                    -1, WindowsRegistry.AutoBackupWindow.max_backups_label.text().find(str(new_max_backups)),
                    f"Expected max backups amount in label is {new_max_backups} returned \
                    {WindowsRegistry.AutoBackupWindow.max_backups_label.text()}"
                )

                WindowsRegistry.AutoBackupWindow.done(0)
                WindowsRegistry.BackupManagementWindow.done(0)
                WindowsRegistry.SettingsWindow.done(0)
            
            qsleep(500)
            QTimer.singleShot(200, self.catch_failure(_check_max_backups_change))
            WindowsRegistry.AutoBackupWindow.max_backups.setText(str(new_max_backups))
            self.click_on_widget(WindowsRegistry.AutoBackupWindow.save)

        self.open_auto_backup_window(_try_to_change_max_backups)

                    


            
