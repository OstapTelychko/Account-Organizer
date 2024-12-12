import os

from alembic.config import Config
from alembic import command
from types import FunctionType
from unittest import  TestSuite, TestLoader, TextTestRunner

from AppObjects.session import Session
from backend.db_controller import DBController
from project_configuration import TEST_DB_PATH, ROOT_DIRECTORY

from tests.test_GUI.test_main_window import TestMainWindow
from tests.test_GUI.test_category import TestCategory
from tests.test_GUI.test_account import TestAccount
from tests.test_GUI.test_transaction import TestTransaction
from tests.test_GUI.test_statistics import TestStatistics


TEST_DB_FILE_PATH = TEST_DB_PATH.replace("sqlite:///","")

def test_main(app_main:FunctionType):
    Session.test_alembic_config = Config(f"{ROOT_DIRECTORY}/alembic.ini")
    Session.test_alembic_config.set_main_option("script_location", f"{ROOT_DIRECTORY}/alembic")
    Session.test_alembic_config.set_main_option("sqlalchemy.url", TEST_DB_PATH)
    command.upgrade(Session.test_alembic_config, "head")

    Session.test_mode = True
    Session.load_user_config()
    previous_name = Session.account_name
    user_name = "Test user"
    Session.account_name = user_name
    Session.update_user_config()

    Session.db = DBController(user_name)
    Session.db.create_account(0)

    app_main()

    try:
        suite = TestSuite()
        loader = TestLoader()
        suite.addTests((loader.loadTestsFromTestCase(TestMainWindow), loader.loadTestsFromTestCase(TestCategory), loader.loadTestsFromTestCase(TestAccount), loader.loadTestsFromTestCase(TestTransaction), loader.loadTestsFromTestCase(TestStatistics)))
        print(f"Tests found: {suite.countTestCases()}")

        TextTestRunner().run(suite)

    except Exception as ex:
        print(ex)

    finally:
        Session.account_name = previous_name
        Session.update_user_config()

        if os.path.exists(TEST_DB_FILE_PATH):
            os.remove(TEST_DB_FILE_PATH)
            
        quit()