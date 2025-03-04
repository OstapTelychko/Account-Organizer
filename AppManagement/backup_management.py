import os
import shutil
from datetime import datetime
from PySide6.QtWidgets import QHeaderView, QCheckBox
from PySide6.QtCore import QTimer, Qt

from languages import LANGUAGES
from DesktopQtToolkit.table_widget import CustomTableWidgetItem
from project_configuration import BACKUPS_DIRECTORY, TEST_BACKUPS_DIRECTORY, MIN_RECOMMENDED_BACKUPS, MAX_RECOMMENDED_BACKUPS, DB_FILE_PATH, TEST_DB_FILE_PATH, MIN_RECOMMENDED_LEGACY_BACKUPS, MAX_RECOMMENDED_LEGACY_BACKUPS, BACKUPS_DATE_FORMAT
from backend.db_controller import DBController
from AppManagement.account import load_account_data

from AppObjects.session import Session
from AppObjects.backup import Backup
from AppObjects.logger import get_logger

from GUI.gui_constants import ALIGNMENT
from GUI.windows.backup_management import BackupManagementWindow, AutoBackupWindow
from GUI.windows.messages import Messages
from GUI.windows.settings import SettingsWindow



logger = get_logger(__name__)

def load_backups():
    BackupManagementWindow.backups_table.setRowCount(0)
    BackupManagementWindow.backups_table.setRowCount(len(Session.backups))
    
    backups_sorted_by_date = sorted(Session.backups.items(), key=lambda backup: datetime.strptime(backup[1].timestamp, BACKUPS_DATE_FORMAT), reverse=True)
    backups_sorted_by_app_version = sorted(backups_sorted_by_date, key=lambda backup: (*map(int, backup[1].app_version.split(".")),), reverse=True)
    for row, (backup_id, backup) in enumerate(backups_sorted_by_app_version):
        data = CustomTableWidgetItem(backup.timestamp)
        data.setFlags(~ Qt.ItemFlag.ItemIsEditable)
        data.setTextAlignment(ALIGNMENT.AlignCenter)

        app_version = CustomTableWidgetItem(backup.app_version)
        app_version.setFlags(~ Qt.ItemFlag.ItemIsEditable)
        app_version.setTextAlignment(ALIGNMENT.AlignCenter)

        BackupManagementWindow.backups_table.setItem(row, 0, data)
        BackupManagementWindow.backups_table.setItem(row, 1, app_version)
        BackupManagementWindow.backups_table.setItem(row, 2, CustomTableWidgetItem(backup_id))
        logger.debug(f"Backup {backup.timestamp} loaded into list")


def create_backup():
    app_version = Session.app_version
    timestamp = datetime.now().strftime(BACKUPS_DATE_FORMAT)

    if Session.test_mode:
        backup_name = os.path.join(TEST_BACKUPS_DIRECTORY, f"Accounts_{timestamp}_{app_version}.sqlite")
    else:
        backup_name = os.path.join(BACKUPS_DIRECTORY, f"Accounts_{timestamp}_{app_version}.sqlite")

    Session.db.create_backup(backup_name)
    backup = Backup(backup_name, timestamp, app_version)
    Session.backups[str(id(backup))] = backup

    def enable_button():
        BackupManagementWindow.create_backup.setEnabled(True)
    BackupManagementWindow.create_backup.setEnabled(False)

    load_backups()
    QTimer.singleShot(1000, enable_button)


def remove_backup():
    selected_items = BackupManagementWindow.backups_table.selectedItems()

    if len(selected_items) == 0 or len(selected_items) < 2:
        return Messages.unselected_row.exec()

    if len(selected_items) > 2 or selected_items[0].row() != selected_items[1].row():
        return Messages.only_one_row.exec()

    if len(Session.backups)-1 < MIN_RECOMMENDED_BACKUPS:
        Messages.below_recommended_min_backups.exec()
        if Messages.below_recommended_min_backups.clickedButton() != Messages.below_recommended_min_backups.ok_button:
            return
    
    else:
        Messages.delete_buckup_confirmation.exec()
        if Messages.delete_buckup_confirmation.clickedButton() != Messages.delete_buckup_confirmation.ok_button:
            return
    
    row = selected_items[0].row()
    backup = Session.backups[BackupManagementWindow.backups_table.item(row, 2).text()]


    del Session.backups[str(id(backup))]
    BackupManagementWindow.backups_table.removeRow(row)
    os.remove(backup.db_file_path)
    
    columns = BackupManagementWindow.backups_table.verticalHeader()
    columns.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


def load_backup():
    selected_items = BackupManagementWindow.backups_table.selectedItems()

    if len(selected_items) == 0 or len(selected_items) < 2:
        return Messages.unselected_row.exec()

    if len(selected_items) > 2 or selected_items[0].row() != selected_items[1].row():
        return Messages.only_one_row.exec()

    row = selected_items[0].row()
    backup = Session.backups[BackupManagementWindow.backups_table.item(row, 2).text()]

    if backup.app_version != Session.app_version:
        return Messages.different_app_version.exec()
    
    Messages.load_backup_confirmation.setText(LANGUAGES[Session.language]["Messages"][24].replace("timestamp", backup.timestamp))
    Messages.load_backup_confirmation.exec()
    if Messages.load_backup_confirmation.clickedButton() != Messages.load_backup_confirmation.ok_button:
        return
    
    create_backup()

    Session.db.close_connection()
    if Session.test_mode:
        shutil.copy(backup.db_file_path, TEST_DB_FILE_PATH)
    else:
        shutil.copy(backup.db_file_path, DB_FILE_PATH)
    Session.db = DBController()
    
    backup_accounts = Session.db.get_all_accounts()
    if Session.account_name not in [account.name for account in backup_accounts]:
        Session.account_name = backup_accounts[0].name

    Session.switch_account = False
    SettingsWindow.accounts.clear()
    Session.accounts_list = [account.name for account in backup_accounts]
    
    Session.switch_account = False
    SettingsWindow.accounts.addItems(Session.accounts_list)
    Session.switch_account = False
    SettingsWindow.accounts.setCurrentText(Session.account_name)

    load_backups()
    load_account_data(Session.account_name)
    BackupManagementWindow.window.done(0)
    SettingsWindow.window.done(0)


def auto_backup():
    if len(Session.backups) == 0:
        create_backup()
        return
    
    backup = Session.backups[BackupManagementWindow.backups_table.item(0, 2).text()]
    backup_date = datetime.strptime(backup.timestamp, BACKUPS_DATE_FORMAT)
    current_date = datetime.now()

    if Session.auto_backup_status == Session.AutoBackupStatus.MONTHLY and backup_date.month != current_date.month:
        create_backup()
        logger.debug("Monthly backup created")

    elif Session.auto_backup_status == Session.AutoBackupStatus.WEEKLY and current_date.isocalendar()[1] != backup_date.isocalendar()[1]:#Week number
        create_backup()
        logger.debug("Weekly backup created")

    elif Session.auto_backup_status == Session.AutoBackupStatus.DAILY and (current_date - backup_date).days >= 1:
        create_backup()
        logger.debug("Daily backup created")


def open_auto_backup_window():
    AutoBackupWindow.monthly.setCheckState(Qt.CheckState.Unchecked)
    AutoBackupWindow.weekly.setCheckState(Qt.CheckState.Unchecked)
    AutoBackupWindow.daily.setCheckState(Qt.CheckState.Unchecked)

    if Session.auto_backup_status == Session.AutoBackupStatus.MONTHLY:
        AutoBackupWindow.monthly.setCheckState(Qt.CheckState.Checked)

    elif Session.auto_backup_status == Session.AutoBackupStatus.WEEKLY:
        AutoBackupWindow.weekly.setCheckState(Qt.CheckState.Checked)

    elif Session.auto_backup_status == Session.AutoBackupStatus.DAILY:
        AutoBackupWindow.daily.setCheckState(Qt.CheckState.Checked)
    
    elif Session.auto_backup_status == Session.AutoBackupStatus.NO_AUTO_BACKUP:
        AutoBackupWindow.no_auto_backup.setCheckState(Qt.CheckState.Checked)
    
    if not Session.auto_backup_removal_enabled:
        AutoBackupWindow.no_auto_removal.setCheckState(Qt.CheckState.Checked)

    AutoBackupWindow.window.exec()


def prevent_same_auto_backup_status(status_checkbox: QCheckBox, state: int):
    if state == 2:#Checked
        if status_checkbox is AutoBackupWindow.monthly:
            AutoBackupWindow.weekly.setCheckState(Qt.CheckState.Unchecked)
            AutoBackupWindow.daily.setCheckState(Qt.CheckState.Unchecked)
            AutoBackupWindow.no_auto_backup.setCheckState(Qt.CheckState.Unchecked)

        elif status_checkbox is AutoBackupWindow.weekly:
            AutoBackupWindow.monthly.setCheckState(Qt.CheckState.Unchecked)
            AutoBackupWindow.daily.setCheckState(Qt.CheckState.Unchecked)
            AutoBackupWindow.no_auto_backup.setCheckState(Qt.CheckState.Unchecked)

        elif status_checkbox is AutoBackupWindow.daily:
            AutoBackupWindow.monthly.setCheckState(Qt.CheckState.Unchecked)
            AutoBackupWindow.weekly.setCheckState(Qt.CheckState.Unchecked)
            AutoBackupWindow.no_auto_backup.setCheckState(Qt.CheckState.Unchecked)
        
        elif status_checkbox is AutoBackupWindow.no_auto_backup:
            AutoBackupWindow.monthly.setCheckState(Qt.CheckState.Unchecked)
            AutoBackupWindow.weekly.setCheckState(Qt.CheckState.Unchecked)
            AutoBackupWindow.daily.setCheckState(Qt.CheckState.Unchecked)


def save_auto_backup_settings():
    if AutoBackupWindow.monthly.isChecked():
        Session.auto_backup_status = Session.AutoBackupStatus.MONTHLY

    elif AutoBackupWindow.weekly.isChecked():
        Session.auto_backup_status = Session.AutoBackupStatus.WEEKLY

    elif AutoBackupWindow.daily.isChecked():
        Session.auto_backup_status = Session.AutoBackupStatus.DAILY
    
    elif AutoBackupWindow.no_auto_backup.isChecked():
        Messages.no_auto_backup.exec()
        if Messages.no_auto_backup.clickedButton() != Messages.no_auto_backup.ok_button:
            return
        Session.auto_backup_status = Session.AutoBackupStatus.NO_AUTO_BACKUP

    Backup_management = LANGUAGES[Session.language]["Windows"]["Settings"]["Backup management"]
    if Session.auto_backup_status == Session.AutoBackupStatus.MONTHLY:
        AutoBackupWindow.current_status.setText(Backup_management[8]+" "+Backup_management[5])
        BackupManagementWindow.auto_backup_status.setText(Backup_management[8]+" "+Backup_management[5])

    elif Session.auto_backup_status == Session.AutoBackupStatus.WEEKLY:
        AutoBackupWindow.current_status.setText(Backup_management[8]+" "+Backup_management[6])
        BackupManagementWindow.auto_backup_status.setText(Backup_management[8]+" "+Backup_management[6])

    elif Session.auto_backup_status == Session.AutoBackupStatus.DAILY:
        AutoBackupWindow.current_status.setText(Backup_management[8]+" "+Backup_management[7])
        BackupManagementWindow.auto_backup_status.setText(Backup_management[8]+" "+Backup_management[7])
    
    elif Session.auto_backup_status == Session.AutoBackupStatus.NO_AUTO_BACKUP:
        AutoBackupWindow.current_status.setText(Backup_management[8]+" "+Backup_management[20])
        BackupManagementWindow.auto_backup_status.setText(Backup_management[8]+" "+Backup_management[20])

    if AutoBackupWindow.no_auto_removal.isChecked():
        if Session.auto_backup_removal_enabled:
            Messages.no_auto_removal.exec()
            if Messages.no_auto_removal.clickedButton() == Messages.no_auto_removal.ok_button:
                Session.auto_backup_removal_enabled = False
    else:
        Session.auto_backup_removal_enabled = True

    new_max_backups = AutoBackupWindow.max_backups.text()
    if new_max_backups:
        if Session.auto_backup_removal_enabled:
            new_max_backups = int(new_max_backups)

            if new_max_backups < MIN_RECOMMENDED_BACKUPS:
                Messages.below_recommended_min_backups.exec()
                if Messages.below_recommended_min_backups.clickedButton() != Messages.below_recommended_min_backups.ok_button:
                    return
            
            elif new_max_backups > MAX_RECOMMENDED_BACKUPS:
                Messages.above_recommended_max_backups.exec()
                if Messages.above_recommended_max_backups.clickedButton() != Messages.above_recommended_max_backups.ok_button:
                    return
            
            Session.max_backups = new_max_backups
            Windows = LANGUAGES[Session.language]["Windows"]
            AutoBackupWindow.max_backups_label.setText(Windows["Settings"]["Backup management"][12].replace("max_backups", str(Session.max_backups)+"\n"+Windows["Settings"]["Backup management"][13]))
        else:
            Messages.auto_removal_disabled.exec()

    new_max_legacy_backups = AutoBackupWindow.max_legacy_backups.text()
    if new_max_legacy_backups:
        if Session.auto_backup_removal_enabled:
            new_max_legacy_backups = int(new_max_legacy_backups)

            if new_max_legacy_backups < MIN_RECOMMENDED_LEGACY_BACKUPS:
                Messages.below_recommended_min_backups.exec()
                if Messages.below_recommended_min_backups.clickedButton() != Messages.below_recommended_min_backups.ok_button:
                    return
            
            elif new_max_legacy_backups > MAX_RECOMMENDED_LEGACY_BACKUPS:
                Messages.above_recommended_max_backups.exec()
                if Messages.above_recommended_max_backups.clickedButton() != Messages.above_recommended_max_backups.ok_button:
                    return
            
            Session.max_legacy_backups = new_max_legacy_backups
            Windows = LANGUAGES[Session.language]["Windows"]
            AutoBackupWindow.max_legacy_backups_label.setText(Windows["Settings"]["Backup management"][17].replace("max_legacy_backups", str(Session.max_legacy_backups)+"\n"+Windows["Settings"]["Backup management"][18]))
        else:
            Messages.auto_removal_disabled.exec()

    if Session.auto_backup_status != Session.AutoBackupStatus.NO_AUTO_BACKUP:
        auto_backup()
    Session.update_user_config()
    AutoBackupWindow.window.done(0)


def auto_remove_backups():
    sorted_backups = sorted(Session.backups.items(), key=lambda backup: datetime.strptime(backup[1].timestamp, BACKUPS_DATE_FORMAT))
    backups = [backup for backup in sorted_backups if backup[1].app_version == Session.app_version]
    legacy_backups = [backup for backup in sorted_backups if backup[1].app_version != Session.app_version]

    if len(backups) != 0:
        for row in range(BackupManagementWindow.backups_table.rowCount()):
            backup_id = BackupManagementWindow.backups_table.item(row, 2).text()
            if backup_id == backups[0][0]:
                supported_backups_row = row

        while len(backups) > Session.max_backups:
            backup_id, backup = backups.pop(0)
            
            os.remove(backup.db_file_path)
            logger.debug(f"Backup {backup.timestamp} removed")
            del Session.backups[backup_id]

            BackupManagementWindow.backups_table.removeRow(supported_backups_row)
            columns = BackupManagementWindow.backups_table.verticalHeader()
            columns.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            supported_backups_row -= 1
    

    if len(legacy_backups) == 0:
        return
    
    for row in range(BackupManagementWindow.backups_table.rowCount()):
        backup_id = BackupManagementWindow.backups_table.item(row, 2).text()
        if backup_id == legacy_backups[0][0]:
            legacy_backups_row = row

    while len(legacy_backups) > Session.max_legacy_backups:
        backup_id, backup = legacy_backups.pop(0)
        
        os.remove(backup.db_file_path)
        logger.debug(f"Legacy backup {backup.timestamp} removed")
        del Session.backups[backup_id]

        BackupManagementWindow.backups_table.removeRow(legacy_backups_row)
        columns = BackupManagementWindow.backups_table.verticalHeader()
        columns.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        legacy_backups_row -= 1