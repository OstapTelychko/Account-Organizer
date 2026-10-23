from __future__ import annotations
from typing import TYPE_CHECKING, Any
import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime import migration
from alembic import command

from project_configuration import DB_PATH, TEST_DB_PATH, APP_DIRECTORY, ALEMBIC_CONFIG_FILE
from AppObjects.logger import get_logger

from backend.models import Account
from backend.account_query import AccountQuery
from backend.category_query import CategoryQuery
from backend.transaction_query import TransactionQuery
from backend.backup_query import BackupQuery
from backend.statistics_query import StatisticsQuery
from backend.search_query import SearchQuery
from backend.reminder_query import ReminderQuery

if TYPE_CHECKING:
    from sqlalchemy import Engine
    from sqlite3 import Connection as SQLiteConnection



logger = get_logger(__name__)

def create_alembic_config(app_directory:str, db_url:str) -> Config:
    """Create the alembic config used by the app. Every alembic config in the app has to be created here.

        Arguments
        ---------
            `app_directory` : (str) - Directory that contains `alembic.ini` and the `alembic` scripts directory.
            `db_url` : (str) - SQLAlchemy URL of the database to migrate.
        Returns
        -------
            `Config` - Alembic config.
    """

    alembic_config = Config(os.path.join(app_directory, ALEMBIC_CONFIG_FILE))
    alembic_config.set_main_option("script_location", os.path.join(app_directory, "alembic"))
    alembic_config.set_main_option("sqlalchemy.url", db_url)
    # Otherwise alembic/env.py runs fileConfig, which disables app loggers and replaces the app log handlers
    alembic_config.attributes["configure_logger"] = False
    return alembic_config


class DBController():
    """
    This class is used to manage the database connection and queries.
    It handles the creation of the database engine, session, and queries
    for accounts, categories, transactions, backups, and statistics.
    """

    def __init__(self, test_mode:bool, test_alembic_config:Config|None = None) -> None:
        # Init db connection 

        if test_mode:
            self.engine = create_engine(TEST_DB_PATH)

            if not test_alembic_config:
                logger.error("Test mode is enabled, but no test_alembic_config provided.")
                raise RuntimeError("Test mode is enabled, but no test_alembic_config provided.")
            
            self.alembic_config = test_alembic_config
        else:
            self.engine = create_engine(DB_PATH)
            logger.debug("Engine created")
            self.alembic_config = create_alembic_config(APP_DIRECTORY, DB_PATH)
            logger.info("Alembic config loaded")

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection:SQLiteConnection, connection_record:Any) -> None:
            """Set SQLite PRAGMA settings for the connection."""

            cursor = dbapi_connection.cursor()
            # cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=OFF")
            logger.info("PRAGMA synchronous=OFF")
            # Alembic migrations use their own engine, so they keep running without FK enforcement
            cursor.execute("PRAGMA foreign_keys=ON")
            logger.info("PRAGMA foreign_keys=ON")
            cursor.close()

        if not self.db_up_to_date(self.alembic_config, self.engine):
            logger.info("Upgrading database")
            command.upgrade(self.alembic_config, "head")

        self.account_id:int|None = None
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

        self.account_query = AccountQuery(self.session_factory)
        self.category_query = CategoryQuery(self.session_factory)
        self.transaction_query = TransactionQuery(self.session_factory)
        self.backup_query = BackupQuery(self.session_factory, self.engine)
        self.statistics_query = StatisticsQuery(self.session_factory)
        self.search_query = SearchQuery(self.session_factory)
        self.reminder_query = ReminderQuery(self.session_factory)

        logger.info("Db session created")


    def close_connection(self) -> None:
        """Close the database connection."""

        logger.info("Closing db connection")
        self.engine.dispose(close=True)
        logger.info("Db connection closed")


    @staticmethod
    def db_up_to_date(alembic_config:Config, engine:Engine) -> bool:
        """Check if the database is up to date with the latest migrations.

            Arguments
            ---------
                `alembic_config` : (Config) - Alembic configuration object.
                `engine` : (Engine) - SQLAlchemy engine object.
            Returns
            -------
                `bool` - True if the database is up to date, False otherwise.
        """

        directory = ScriptDirectory.from_config(alembic_config)

        with engine.begin() as connection:
            logging.getLogger("alembic.runtime.migration").setLevel(logging.WARN)
            context = migration.MigrationContext.configure(connection)
            logging.getLogger("alembic.runtime.migration").setLevel(logging.INFO)
            
            return set(context.get_current_heads()) == set(directory.get_heads())


    def set_account_id(self, account_name:str) -> None:
        """Set the account ID based on the account name.

            Arguments
            ---------
                `account_name` : (str) - Name of the account to set.
        """
        
        with self.session_factory() as session:
            with session.begin():
                account = session.query(Account).filter(Account.name == account_name).first()
                if not account:
                    logger.error(f"Account with name {account_name} not found.")
                    raise ValueError(f"Account with name '{account_name}' not found.")
                
                self.account_id = account.id
                self.account_query.account_id = self.account_id
                self.category_query.account_id = self.account_id
                self.transaction_query.account_id = self.account_id
                self.backup_query.account_id = self.account_id
                self.statistics_query.account_id = self.account_id
                self.reminder_query.account_id = self.account_id
    

    def create_account(self, account_name:str, balance:float|int=0) -> None:
        """Create a new account in the database.

            Arguments
            ---------
                `account_name` : (str) - Name of the account to create.
                `balance` : (float|int) - Initial balance of the account. Default is 0.
        """

        self.account_query.create_account(account_name, balance)
        self.set_account_id(account_name)