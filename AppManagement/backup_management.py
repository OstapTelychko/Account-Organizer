import os
from datetime import datetime
from PySide6.QtCore import QTimer, Qt

from DesktopQtToolkit.table_widget import CustomTableWidgetItem
from project_configuration import BACKUPS_DIRECTORY
from AppObjects.session import Session
from AppObjects.backup import Backup

from GUI.windows.backup_management import BackupManagement
from GUI.gui_constants import ALIGNMENT


def load_backups():
    BackupManagement.backups_table.sortItems(-1, Qt.SortOrder.DescendingOrder)
    BackupManagement.backups_table.setRowCount(0)
    BackupManagement.backups_table.setRowCount(len(Session.backups))

    for row, backup in enumerate(Session.backups):
        data = CustomTableWidgetItem(backup.timestamp)
        data.setFlags(~ Qt.ItemFlag.ItemIsEditable)
        data.setTextAlignment(ALIGNMENT.AlignCenter)

        app_version = CustomTableWidgetItem(backup.app_version)
        app_version.setFlags(~ Qt.ItemFlag.ItemIsEditable)
        app_version.setTextAlignment(ALIGNMENT.AlignCenter)

        BackupManagement.backups_table.setItem(row, 0, data)
        BackupManagement.backups_table.setItem(row, 1, app_version)

    BackupManagement.backups_table.sortItems(0, Qt.SortOrder.DescendingOrder)



def create_backup():
    app_version = ".".join(map(str, Session.app_version))
    timestamp = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    backup_name = os.path.join(BACKUPS_DIRECTORY, f"Accounts_{timestamp}_{app_version}.sqlite")

    Session.db.create_backup(backup_name)
    Session.backups.append(Backup(backup_name, timestamp, app_version))

    def enable_button():
        BackupManagement.create_backup.setEnabled(True)
    BackupManagement.create_backup.setEnabled(False)

    load_backups()
    QTimer.singleShot(1000, enable_button)