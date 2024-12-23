import os
from datetime import datetime
from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import QTimer, Qt

from DesktopQtToolkit.table_widget import CustomTableWidgetItem
from project_configuration import BACKUPS_DIRECTORY, MIN_RECOMMENDED_BACKUPS
from AppObjects.session import Session
from AppObjects.backup import Backup

from GUI.gui_constants import ALIGNMENT
from GUI.windows.backup_management import BackupManagement
from GUI.windows.messages import Messages


def load_backups():
    BackupManagement.backups_table.sortItems(-1, Qt.SortOrder.DescendingOrder)
    BackupManagement.backups_table.setRowCount(0)
    BackupManagement.backups_table.setRowCount(len(Session.backups))

    for row, (backup_id, backup) in enumerate(Session.backups.items()):
        data = CustomTableWidgetItem(backup.timestamp)
        data.setFlags(~ Qt.ItemFlag.ItemIsEditable)
        data.setTextAlignment(ALIGNMENT.AlignCenter)

        app_version = CustomTableWidgetItem(backup.app_version)
        app_version.setFlags(~ Qt.ItemFlag.ItemIsEditable)
        app_version.setTextAlignment(ALIGNMENT.AlignCenter)


        BackupManagement.backups_table.setItem(row, 0, data)
        BackupManagement.backups_table.setItem(row, 1, app_version)
        BackupManagement.backups_table.setItem(row, 2, CustomTableWidgetItem(backup_id))

    BackupManagement.backups_table.sortItems(0, Qt.SortOrder.DescendingOrder)


def create_backup():
    app_version = ".".join(map(str, Session.app_version))
    timestamp = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    backup_name = os.path.join(BACKUPS_DIRECTORY, f"Accounts_{timestamp}_{app_version}.sqlite")

    Session.db.create_backup(backup_name)
    backup = Backup(backup_name, timestamp, app_version)
    Session.backups[str(id(backup))] = backup

    def enable_button():
        BackupManagement.create_backup.setEnabled(True)
    BackupManagement.create_backup.setEnabled(False)

    load_backups()
    QTimer.singleShot(1000, enable_button)


def remove_backup():
    selected_items = BackupManagement.backups_table.selectedItems()

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
    backup = Session.backups[BackupManagement.backups_table.item(row, 2).text()]


    os.remove(backup.db_file_path)
    del Session.backups[str(id(backup))]
    BackupManagement.backups_table.removeRow(row)
    
    columns = BackupManagement.backups_table.verticalHeader()
    columns.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
