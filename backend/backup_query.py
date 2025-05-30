from __future__ import annotations
from typing import TYPE_CHECKING
from sqlite3 import connect as sql_connect
from AppObjects.logger import get_logger

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker, Session as sql_Session
    from sqlalchemy import Engine


logger = get_logger(__name__)

class BackupQuery:
    """This class is used to manage the backup logic of the database.
    It contains methods to create a backup of the database and to restore the database from a backup."""

    def __init__(self, session_factory:sessionmaker[sql_Session], engine:Engine) -> None:
        self.session_factory = session_factory
        self.engine = engine
        self.account_id:int
    

    def create_backup(self, backup_file_path:str) -> None:
        """Create a backup of the database.
        
            Arguments
            ---------
                `backup_file_path` : (str) - Path to the backup file.
        """

        if self.engine.url.database is not None:
            db_file_path = self.engine.url.database.replace("sqlite:///", "")

            conn = None
            backup_conn = None
            try:
                with sql_connect(db_file_path) as conn:
                    conn.execute("PRAGMA VACUUM")

                    with sql_connect(backup_file_path) as backup_conn:
                        conn.backup(backup_conn)
            finally:
                if conn:
                    conn.close()
                if backup_conn:
                    backup_conn.close()

        else:
            logger.error("Database file path is None. Cannot create backup.")


    def create_backup_based_on_external_db(self, external_db_path:str, backup_file_path:str) -> None:
        """Create a backup of the database based on an external database.
        
            Arguments
            ---------
                `external_db_path` : (str) - Path to the external database file.
                `backup_file_path` : (str) - Path to the backup file.
        """

        conn = None
        backup_conn = None
        try:
            with sql_connect(external_db_path) as conn:
                with sql_connect(backup_file_path) as backup_conn:
                    conn.backup(backup_conn)
        finally:
            if conn:
                conn.close()
            if backup_conn:
                backup_conn.close()
