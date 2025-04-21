from __future__ import annotations
from typing import TYPE_CHECKING
import os
import shutil
from unittest import  TestSuite, TestLoader, TextTestRunner

from alembic.config import Config
from alembic import command

from AppObjects.user_config import UserConfig
from AppObjects.session import Session
from backend.db_controller import DBController
from project_configuration import TEST_DB_PATH, APP_DIRECTORY, TEST_DB_FILE_PATH, TEST_BACKUPS_DIRECTORY, TEST_USER_CONF_PATH

from tests.app_tests.test_main_window import TestMainWindow
from tests.app_tests.test_category import TestCategory
from tests.app_tests.test_account import TestAccount
from tests.app_tests.test_transaction import TestTransaction
from tests.app_tests.test_statistics import TestStatistics
from tests.app_tests.test_backups_management import TestBackupsManagement
from tests.app_tests.test_shortcuts import TestShortcuts

from tests.tests_toolkit import ColoredTextTestResult

if TYPE_CHECKING:
    from typing import Callable




def test_main(app_main:Callable[[], None]):
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
    Session.config = UserConfig(Session.test_mode)
    Session.config.create_user_config()
    Session.config.load_user_config()
    user_name = "Test user"
    Session.config.account_name = user_name
    Session.config.update_user_config()

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
        loader.loadTestsFromTestCase(TestBackupsManagement),
        loader.loadTestsFromTestCase(TestShortcuts),
        ))
        
        print(f"Tests found: {suite.countTestCases()}")

        TextTestRunner(resultclass=ColoredTextTestResult).run(suite)

    except Exception as ex:
        print(ex)

    finally:
        Session.db.close_connection()

        os.remove(TEST_USER_CONF_PATH)

        if os.path.exists(TEST_BACKUPS_DIRECTORY):
            shutil.rmtree(TEST_BACKUPS_DIRECTORY)

        os._exit(0)
        