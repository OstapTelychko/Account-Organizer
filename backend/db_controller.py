from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime import migration
from alembic import command

from project_configuration import DB_PATH, TEST_DB_PATH, APP_DIRECTORY
from AppObjects.logger import get_logger
from AppObjects.session import Session

from backend.models import Account
from backend.account_query import AccountQuery
from backend.category_query import CategoryQuery
from backend.transaction_query import TransactionQuery
from backend.backup_query import BackupQuery
from backend.statistics_query import StatisticsQuery

if TYPE_CHECKING:
    from sqlalchemy import Engine

logger = get_logger(__name__)

class DBController():

    def __init__(self):
        # Init db connection 

        logger.info("Loadin alembic config")
        self.alembic_config = Config(f"{APP_DIRECTORY}/alembic.ini")
        self.alembic_config.set_main_option("script_location", f"{APP_DIRECTORY}/alembic")
        self.alembic_config.set_main_option("sqlalchemy.url", DB_PATH)

        if Session.test_mode:
            self.engine = create_engine(TEST_DB_PATH)
            self.alembic_config = Session.test_alembic_config
        else:
            self.engine = create_engine(DB_PATH)
            logger.debug("Engine created")

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            # cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=OFF")
            logger.info("PRAGMA synchronous=OFF")
            cursor.close()

        if not self.db_up_to_date(self.alembic_config, self.engine):
            logger.info("Upgrading database")
            command.upgrade(self.alembic_config, "head")

        self.account_id = None
        self.session = sessionmaker(bind=self.engine)()

        self.account_query = AccountQuery(self.session)
        self.category_query = CategoryQuery(self.session)
        self.transaction_query = TransactionQuery(self.session)
        self.backup_query = BackupQuery(self.session, self.engine)
        self.statistics_query = StatisticsQuery(self.session)

        logger.info("Db session created")


    def close_connection(self):
        logger.info("Closing db connection")
        try:
            self.session.commit()
            logger.info("Db session commited")
        except:
            self.session.rollback()
            logger.error("Rollback")
        finally:
            self.session.expire_all()
            self.session.close()
            self.engine.dispose(close=True)
            logger.info("Db connection closed")


    @staticmethod
    def db_up_to_date(alembic_config:Config, engine:Engine) -> bool:
        directory = ScriptDirectory.from_config(alembic_config)

        with engine.begin() as connection:
            logging.getLogger("alembic.runtime.migration").setLevel(logging.WARN)
            context = migration.MigrationContext.configure(connection)
            logging.getLogger("alembic.runtime.migration").setLevel(logging.INFO)
            return set(context.get_current_heads()) == set(directory.get_heads())


    def set_account_id(self, account_name:str):
        self.account_id = self.session.query(Account).filter(Account.name == account_name).first().id
        self.account_query.account_id = self.account_id
        self.category_query.account_id = self.account_id
        self.transaction_query.account_id = self.account_id
        self.backup_query.account_id = self.account_id
        self.statistics_query.account_id = self.account_id
    

    def create_account(self, account_name:str, balance:float|int=0):
        self.account_query.create_account(account_name, balance)
        self.set_account_id(account_name)