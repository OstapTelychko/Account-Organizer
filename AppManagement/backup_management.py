import os
import shutil
from datetime import datetime
from PySide6.QtWidgets import QHeaderView, QCheckBox
from PySide6.QtCore import QTimer, Qt

from languages import LANGUAGES
from DesktopQtToolkit.table_widget import CustomTableWidgetItem
from project_configuration import BACKUPS_DIRECTORY, TEST_BACKUPS_DIRECTORY, MIN_RECOMMENDED_BACKUPS, DB_FILE_PATH, TEST_DB_FILE_PATH
from backend.db_controller import DBController
from AppManagement.account import load_account_data

from AppObjects.session import Session
from AppObjects.backup import Backup

from GUI.gui_constants import ALIGNMENT
from GUI.windows.backup_management import BackupManagementWindow, AutoBackupWindow
from GUI.windows.messages import Messages
from GUI.windows.settings import SettingsWindow


def load_backups():
    BackupManagementWindow.backups_table.setRowCount(0)
    BackupManagementWindow.backups_table.setRowCount(len(Session.backups))
    
    backups = sorted(Session.backups.items(), key=lambda backup: datetime.strptime(backup[1].timestamp, "%d-%m-%Y_%H:%M:%S"), reverse=True)
    for row, (backup_id, backup) in enumerate(backups):
        data = CustomTableWidgetItem(backup.timestamp)
        data.setFlags(~ Qt.ItemFlag.ItemIsEditable)
        data.setTextAlignment(ALIGNMENT.AlignCenter)

        app_version = CustomTableWidgetItem(backup.app_version)
        app_version.setFlags(~ Qt.ItemFlag.ItemIsEditable)
        app_version.setTextAlignment(ALIGNMENT.AlignCenter)

        BackupManagementWindow.backups_table.setItem(row, 0, data)
        BackupManagementWindow.backups_table.setItem(row, 1, app_version)
        BackupManagementWindow.backups_table.setItem(row, 2, CustomTableWidgetItem(backup_id))


def create_backup():
    app_version = ".".join(map(str, Session.app_version))
    timestamp = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")

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
        Messages.below_min_backups.exec()
        if Messages.below_min_backups.clickedButton() != Messages.below_min_backups.ok_button:
            return
    
    else:
        Messages.delete_buckup_confirmation.exec()
        if Messages.delete_buckup_confirmation.clickedButton() != Messages.delete_buckup_confirmation.ok_button:
            return
    
    row = selected_items[0].row()
    backup = Session.backups[BackupManagementWindow.backups_table.item(row, 2).text()]


    os.remove(backup.db_file_path)
    del Session.backups[str(id(backup))]
    BackupManagementWindow.backups_table.removeRow(row)
    
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

    if backup.app_version != ".".join(map(str, Session.app_version)):
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
    backup_date = datetime.strptime(backup.timestamp, "%d-%m-%Y_%H:%M:%S")
    current_date = datetime.now()
    

    if Session.auto_backup_status == Session.AutoBackupStatus.MONTHLY and backup_date.month != current_date.month:
        create_backup()

    elif Session.auto_backup_status == Session.AutoBackupStatus.WEEKLY and current_date.isocalendar()[1] != backup_date.isocalendar()[1]:#Week number
        create_backup()

    elif Session.auto_backup_status == Session.AutoBackupStatus.DAILY and (current_date - backup_date).days >= 1:
        create_backup()


def prevent_same_auto_backup_status(status_checkbox: QCheckBox, state: int):
    if state == 2:#Checked
        if status_checkbox is AutoBackupWindow.monthly:
            AutoBackupWindow.weekly.setCheckState(Qt.CheckState.Unchecked)
            AutoBackupWindow.daily.setCheckState(Qt.CheckState.Unchecked)

        elif status_checkbox is AutoBackupWindow.weekly:
            AutoBackupWindow.monthly.setCheckState(Qt.CheckState.Unchecked)
            AutoBackupWindow.daily.setCheckState(Qt.CheckState.Unchecked)

        else:
            AutoBackupWindow.monthly.setCheckState(Qt.CheckState.Unchecked)
            AutoBackupWindow.weekly.setCheckState(Qt.CheckState.Unchecked)


def save_auto_backup_status():
    if AutoBackupWindow.monthly.isChecked():
        Session.auto_backup_status = Session.AutoBackupStatus.MONTHLY

    elif AutoBackupWindow.weekly.isChecked():
        Session.auto_backup_status = Session.AutoBackupStatus.WEEKLY

    else:
        Session.auto_backup_status = Session.AutoBackupStatus.DAILY

    Backup_management = LANGUAGES[Session.language]["Windows"]["Settings"]["Backup management"]
    if Session.auto_backup_status == Session.AutoBackupStatus.MONTHLY:
        AutoBackupWindow.current_status.setText(Backup_management[8]+" "+Backup_management[5])
        BackupManagementWindow.auto_backup_status.setText(Backup_management[8]+" "+Backup_management[5])

    elif Session.auto_backup_status == Session.AutoBackupStatus.WEEKLY:
        AutoBackupWindow.current_status.setText(Backup_management[8]+" "+Backup_management[6])
        BackupManagementWindow.auto_backup_status.setText(Backup_management[8]+" "+Backup_management[6])

    else:
        AutoBackupWindow.current_status.setText(Backup_management[8]+" "+Backup_management[7])
        BackupManagementWindow.auto_backup_status.setText(Backup_management[8]+" "+Backup_management[7])

    auto_backup()
    Session.update_user_config()
    AutoBackupWindow.window.done(0)