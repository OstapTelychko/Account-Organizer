from __future__ import annotations
from typing import TYPE_CHECKING
import os
import shutil
from unittest import  TestSuite, TestLoader, TextTestRunner

from alembic.config import Config
from alembic import command

from AppObjects.session import Session
from backend.db_controller import DBController
from project_configuration import TEST_DB_PATH, APP_DIRECTORY, TEST_DB_FILE_PATH, TEST_BACKUPS_DIRECTORY, TEST_USER_CONF_PATH

from tests.app_tests.test_main_window import TestMainWindow
from tests.app_tests.test_category import TestCategory
from tests.app_tests.test_account import TestAccount
from tests.app_tests.test_transaction import TestTransaction
from tests.app_tests.test_statistics import TestStatistics
from tests.app_tests.test_backups_management import TestBackupsManagement

if TYPE_CHECKING:
    from types import FunctionType


def test_main(app_main:FunctionType):
    """This function is used to run the tests in the test suite.
        Arguments
        ---------
            `app_main` : (FunctionType) - Main function of the application.
    """

    if os.path.exists(TEST_DB_FILE_PATH):#Why not remove test db at the end? Because of windows file locking system (lock db even if all connections are closed)
        os.remove(TEST_DB_FILE_PATH)

    if os.path.exists(TEST_BACKUPS_DIRECTORY):
        shutil.rmtree(TEST_BACKUPS_DIRECTORY)
    
    Session.test_alembic_config = Config(f"{APP_DIRECTORY}/alembic.ini")
    Session.test_alembic_config.set_main_option("script_location", f"{APP_DIRECTORY}/alembic")
    Session.test_alembic_config.set_main_option("sqlalchemy.url", TEST_DB_PATH)
    command.upgrade(Session.test_alembic_config, "head")

    Session.test_mode = True
    Session.create_user_config()
    Session.load_user_config()
    # previous_name = Session.account_name
    user_name = "Test user"
    Session.account_name = user_name
    Session.update_user_config()

    Session.db = DBController()
    Session.db.create_account(user_name, 0)

    app_main()

    try:
        suite = TestSuite()
        loader = TestLoader()
        suite.addTests((
        loader.loadTestsFromTestCase(TestMainWindow),
        loader.loadTestsFromTestCase(TestCategory),
        loader.loadTestsFromTestCase(TestAccount),
        loader.loadTestsFromTestCase(TestTransaction),
        loader.loadTestsFromTestCase(TestStatistics),
        loader.loadTestsFromTestCase(TestBackupsManagement)))
        print(f"Tests found: {suite.countTestCases()}")

        TextTestRunner().run(suite)

    except Exception as ex:
        print(ex)

    finally:
        # Session.account_name = previous_name
        # Session.update_user_config()
        Session.db.close_connection()

        os.remove(TEST_USER_CONF_PATH)

        if os.path.exists(TEST_BACKUPS_DIRECTORY):
            shutil.rmtree(TEST_BACKUPS_DIRECTORY)

        os._exit(0)
        