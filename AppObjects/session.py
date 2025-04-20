from __future__ import annotations
import toml
import os
import sys
from typing import TYPE_CHECKING
from datetime import datetime
from enum import Enum

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication

from project_configuration import USER_CONF_PATH, APP_DIRECTORY, BACKUPS_DIRECTORY, TEST_BACKUPS_DIRECTORY, MAX_RECOMMENDED_BACKUPS, \
MAX_RECOMMENDED_LEGACY_BACKUPS, DEVELOPMENT_MODE, ERROR_LOG_FILE, TEST_USER_CONF_PATH, ERROR_LOG_START_MESSAGE

from AppObjects.single_instance_guard import SingleInstanceGuard
from AppObjects.backup import Backup
from AppObjects.user_config import UserConfig
from AppObjects.logger import get_logger

if TYPE_CHECKING:
    from alembic.config import Config
    from types import TracebackType
    
    from backend.models import Account
    from backend.db_controller import DBController
    from GUI.windows.account import SwitchAccountWindow
    from AppObjects.category import Category



logger = get_logger(__name__)

class Session:
    """Global application state and services". It stores all session variables and methods. Used to load user configuration, app version, and backups."""

    app_version:str

    current_month = 4
    current_year = 2023
    current_balance = 0
    current_total_income = 0
    current_total_expenses = 0

    accounts_list:list[Account] = []
    categories:dict[int, Category] = {}
    focused_income_category:Category
    focused_expense_category:Category

    account_switch_widgets:list[SwitchAccountWindow.AccountSwitchWidget] = []

    db:DBController
    backups:dict[str, Backup] = {}

    instance_guard:SingleInstanceGuard
    test_mode = False
    test_alembic_config:Config

    config:UserConfig

 
    @staticmethod
    def start_session():
        """Start session. It loads user configuration, app version, and backups. It also sets the current date and creates the backups directory if it doesn't exist."""

        logger.info("__BREAK_LINE__")
        logger.info("__BREAK_LINE__")
        logger.info("Starting session")
        logger.error("__BREAK_LINE__")
        logger.error("__BREAK_LINE__")
        logger.error(ERROR_LOG_START_MESSAGE)
        sys.excepthook = Session.custom_excepthook
        Session.instance_guard = SingleInstanceGuard()

        if Session.instance_guard.is_running:
            print("Another instance is already running. Exiting.")
            logger.info("Ending session")
            sys.exit(0)
        
        Session.load_app_version()
        logger.debug(f"App version: {Session.app_version}")
            
        #Set current date
        Session.current_month = datetime.now().month
        Session.current_year = datetime.now().year
        logger.debug(f"Current month: {Session.current_month}, current year: {Session.current_year}")
        
        Session.config = UserConfig(Session.test_mode)

        if not os.path.exists(USER_CONF_PATH):
            Session.config.create_user_config()
            logger.info("User configuration file created")

        Session.config.load_user_config()
        logger.info("User configuration loaded")
        if Session.test_mode:
            os.makedirs(TEST_BACKUPS_DIRECTORY, exist_ok=True)
        else:
            os.makedirs(BACKUPS_DIRECTORY, exist_ok=True)
        logger.info("Backups directory created")
        Session.load_backups()
        logger.info("Backups loaded")
        logger.info("__BREAK_LINE__")
    

    @staticmethod
    def load_app_version():
        """Load app version from file. It reads the version from the file and sets it to the app_version variable."""

        with open(f"{APP_DIRECTORY}/app version.txt") as file:
            Session.app_version = file.read().strip()

        
    @staticmethod
    def load_backups():
        """Load backups from the backups directory. It loads all backups and adds them to the session."""

        for backup_path in os.listdir(BACKUPS_DIRECTORY) if not Session.test_mode else os.listdir(TEST_BACKUPS_DIRECTORY):
            if Session.test_mode:
                backup = Backup.parse_db_file_path(os.path.join(TEST_BACKUPS_DIRECTORY, backup_path))
            else:
                backup = Backup.parse_db_file_path(os.path.join(BACKUPS_DIRECTORY, backup_path))
            Session.backups[str(id(backup))] = backup
            logger.debug(f"Backup loaded: {backup.db_file_path}")


    @staticmethod
    def end_session():
        """End session. It closes the database connection, removes the instance guard, and closes all sockets."""

        Session.instance_guard.close_sockets()
        Session.db.close_connection()
        logger.info("Ending session")
    

    @staticmethod
    def custom_excepthook(exc_type:type[BaseException], exc_value:BaseException, exc_traceback:TracebackType | None):
        """Custom excepthook. It logs the exception to Error log."""

        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        logger.info(f"Ending session with critical error (see {ERROR_LOG_FILE})\n\n")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


    @staticmethod
    def restart_app():
        """Restart the app. It closes the current session and starts a new one."""

        Session.end_session()
        if DEVELOPMENT_MODE:
            QProcess.startDetached(sys.executable, sys.argv)#First argument using IDE is the path to the script that have to be run 
        else:
            QProcess.startDetached(sys.executable, sys.argv[1:])#First argument in argv is the path to the executable, the second is the list of arguments
        QApplication.quit()
        