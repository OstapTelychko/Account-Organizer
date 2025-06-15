from __future__ import annotations
from typing import TYPE_CHECKING
import os
import shutil
from unittest import  TestSuite, TestLoader, TextTestRunner

from alembic.config import Config
from alembic import command

from AppObjects.user_config import UserConfig
from AppObjects.session import AppCore
from AppObjects.single_instance_guard import SingleInstanceGuard
from backend.db_controller import DBController
from project_configuration import TEST_DB_PATH, APP_DIRECTORY, TEST_DB_FILE_PATH, TEST_BACKUPS_DIRECTORY, TEST_USER_CONF_PATH

from tests.tests_toolkit import ColoredTextTestResult

if TYPE_CHECKING:
    from typing import Callable




def test_main(app_main:Callable[[bool], None]) -> None:
    """This function is used to run the tests in the test suite.

        Arguments
        ---------
            `app_main` : - Main function of the application.
    """

    if os.path.exists(TEST_DB_FILE_PATH):#Why not remove test db at the end? Because of windows file locking system (lock db even if all connections are closed)
        os.remove(TEST_DB_FILE_PATH)

    if os.path.exists(TEST_BACKUPS_DIRECTORY):
        shutil.rmtree(TEST_BACKUPS_DIRECTORY)
    
    test_alembic_config = Config(f"{APP_DIRECTORY}/alembic.ini")
    test_alembic_config.set_main_option("script_location", f"{APP_DIRECTORY}/alembic")
    test_alembic_config.set_main_option("sqlalchemy.url", TEST_DB_PATH)
    command.upgrade(test_alembic_config, "head")

    user_config = UserConfig(True)
    user_config.create_user_config()
    user_config.load_user_config()
    user_name = "Test user"
    user_config.account_name = user_name
    user_config.update_user_config()

    db_controller = DBController(True, test_alembic_config)
    db_controller.create_account(user_name, 0)

    app_core = AppCore(SingleInstanceGuard(), db_controller, user_config, True, test_alembic_config)

    app_main(True)

    from tests.app_tests.test_main_window import TestMainWindow
    from tests.app_tests.test_category import TestCategory
    from tests.app_tests.test_account import TestAccount
    from tests.app_tests.test_transaction import TestTransaction
    from tests.app_tests.test_statistics import TestStatistics
    from tests.app_tests.test_backups_management import TestBackupsManagement
    from tests.app_tests.test_shortcuts import TestShortcuts
    from tests.app_tests.test_update_app import TestUpdateApp

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
        loader.loadTestsFromTestCase(TestUpdateApp),
        ))
        
        print(f"Tests found: {suite.countTestCases()}")

        TextTestRunner(resultclass=ColoredTextTestResult).run(suite) #type: ignore[arg-type] #Mypy doesn't recognize ColoredTextTestResult as a valid type for resultclass

    except Exception as ex:
        print(ex)

    finally:
        app_core.db.close_connection()

        os.remove(TEST_USER_CONF_PATH)

        if os.path.exists(TEST_BACKUPS_DIRECTORY):
            shutil.rmtree(TEST_BACKUPS_DIRECTORY)

        os._exit(0)
        