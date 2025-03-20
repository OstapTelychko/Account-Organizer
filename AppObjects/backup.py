from __future__ import annotations
from pathlib import Path


class Backup:
    def __init__(self, db_file_path:str, timestamp:str, app_version:str):
        self.db_file_path = db_file_path
        self.db_path = f"sqlite:///{db_file_path}"
        self.timestamp = timestamp
        self.app_version = app_version
    

    @staticmethod
    def parse_db_file_path(db_file_path:str) -> Backup:
        db_name = Path(db_file_path).name
        db_name_parts = db_name.split("_")
        timestamp = db_name_parts[1]+"_"+db_name_parts[2]
        app_version = db_name_parts[3].replace(".sqlite", "")

        return Backup(db_file_path, timestamp, app_version)
