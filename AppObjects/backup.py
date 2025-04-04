from __future__ import annotations
from pathlib import Path


class Backup:
    """
    Represents a backup of the database.
    It contains the path to the backup file, the timestamp of the backup, and the app version."""

    def __init__(self, db_file_path:str, timestamp:str, app_version:str):
        self.db_file_path = db_file_path
        self.db_path = f"sqlite:///{db_file_path}"
        self.timestamp = timestamp
        self.app_version = app_version
    

    @staticmethod
    def parse_db_file_path(db_file_path:str) -> Backup:
        """Parse the database file path to create a Backup object.

            Arguments
            ---------
                `db_file_path` : (str) - Path to the database file.
            Returns
            -------
                `Backup` object with the parsed information.
        """

        db_name = Path(db_file_path).name
        db_name_parts = db_name.split("_")
        timestamp = db_name_parts[1]+"_"+db_name_parts[2]
        app_version = db_name_parts[3].replace(".sqlite", "")

        return Backup(db_file_path, timestamp, app_version)
