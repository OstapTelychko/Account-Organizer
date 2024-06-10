import os
from alembic.config import Config
from alembic import command

from unittest import  TestSuite, TestLoader, TextTestRunner, makeSuite

from main import main
from AppObjects.session import Session
from backend.db_controller import DBController
from project_configuration import TEST_DB_PATH, ROOT_DIRECTORY

from tests.test_GUI.test_main_window import TestMainWindow
from tests.test_GUI.test_category import TestCategory
from tests.test_GUI.test_account import TestAccount


TEST_DB_PATH = f"{ROOT_DIRECTORY}/test_Accounts.sqlite"

alembic_conf = Config("alembic.ini")
alembic_conf.set_main_option("sqlalchemy.url", "sqlite:///test_Accounts.sqlite")
command.upgrade(alembic_conf, "head")

Session.test_mode = True
Session.load_user_config()
previous_name = Session.account_name
user_name = "Test user"
Session.account_name = user_name
Session.update_user_config()

Session.db = DBController(user_name)
Session.db.create_account(0)

main()

try:
    suite = TestSuite()
    loader = TestLoader()
    suite.addTests((makeSuite(TestMainWindow), makeSuite(TestCategory), makeSuite(TestAccount)))

    TextTestRunner().run(suite)

except Exception as ex:
    print(ex)

finally:
    Session.account_name = previous_name
    Session.update_user_config()

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        
    quit()