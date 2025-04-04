from __future__ import annotations
from typing import TYPE_CHECKING
from sqlite3 import connect as sql_connect

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as sql_Session
    from sqlalchemy import Engine



class BackupQuery:
    """This class is used to manage the backup logic of the database.
    It contains methods to create a backup of the database and to restore the database from a backup."""

    def __init__(self, session:sql_Session, engine:Engine):
        self.session = session
        self.engine = engine
        self.account_id:int = None
    

    def create_backup(self, backup_file_path:str ):
        """Create a backup of the database.
        
            Arguments
            ---------
                `backup_file_path` : (str) - Path to the backup file.
        """

        db_file_path = self.engine.url.database.replace("sqlite:///", "")
        try:
            with sql_connect(db_file_path) as conn:
                conn.execute("PRAGMA VACUUM")

                with sql_connect(backup_file_path) as backup_conn:
                    conn.backup(backup_conn)
        finally:
            conn.close()
            backup_conn.close()


    def create_backup_based_on_external_db(self, external_db_path:str, backup_file_path:str):
        """Create a backup of the database based on an external database.
        
            Arguments
            ---------
                `external_db_path` : (str) - Path to the external database file.
                `backup_file_path` : (str) - Path to the backup file.
        """

        try:
            with sql_connect(external_db_path) as conn:
                with sql_connect(backup_file_path) as backup_conn:
                    conn.backup(backup_conn)
        finally:
            conn.close()
            backup_conn.close()