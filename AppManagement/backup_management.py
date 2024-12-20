import os
from pathlib import Path
from PySide6.QtCore import QTimer, Qt

from DesktopQtToolkit.table_widget import CustomTableWidgetItem
from project_configuration import BACKUPS_DIRECTORY
from AppObjects.session import Session

from GUI.windows.backup_management import BackupManagement
from GUI.gui_constants import ALIGNMENT


def load_backups():
    BackupManagement.backups_table.sortItems(-1, Qt.SortOrder.DescendingOrder)
    BackupManagement.backups_table.setRowCount(0)

    backups = [Path(backup).name for backup in os.listdir(BACKUPS_DIRECTORY)]
    BackupManagement.backups_table.setRowCount(len(backups))
    backups_dates = [backup.split("_")[1]+"_"+":".join(backup.split("_")[2].split("-")) for backup in backups]
    backups_app_versions = [backup.split("_")[3].replace(".sqlite", "") for backup in backups]

    for row, (date, app_version) in enumerate(zip(backups_dates, backups_app_versions)):
        data = CustomTableWidgetItem(date)
        data.setFlags(~ Qt.ItemFlag.ItemIsEditable)
        data.setTextAlignment(ALIGNMENT.AlignCenter)

        app_version = CustomTableWidgetItem(app_version)
        app_version.setFlags(~ Qt.ItemFlag.ItemIsEditable)
        app_version.setTextAlignment(ALIGNMENT.AlignCenter)

        BackupManagement.backups_table.setItem(row, 0, data)
        BackupManagement.backups_table.setItem(row, 1, app_version)

    BackupManagement.backups_table.sortItems(0, Qt.SortOrder.DescendingOrder)



def create_backup():
    Session.db.create_backup(Session.app_version)

    def enable_button():
        BackupManagement.create_backup.setEnabled(True)
    BackupManagement.create_backup.setEnabled(False)

    load_backups()
    QTimer.singleShot(1000, enable_button)