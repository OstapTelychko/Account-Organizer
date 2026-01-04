from __future__ import annotations
import os
import sys
from typing import TYPE_CHECKING
from datetime import datetime

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication

from project_configuration import USER_CONF_PATH, APP_DIRECTORY, BACKUPS_DIRECTORY, TEST_BACKUPS_DIRECTORY,\
DEVELOPMENT_MODE, ERROR_LOG_FILE, ERROR_LOG_START_MESSAGE, APP_HASHES_DIRECTORY, CACHE_DIRECTORY, VERSION_FILE_NAME

from AppObjects.single_instance_guard import SingleInstanceGuard
from AppObjects.backup import Backup
from AppObjects.user_config import UserConfig
from AppObjects.logger import get_logger

if TYPE_CHECKING:
    from alembic.config import Config
    from typing import Any
    from types import TracebackType
    
    from backend.models import Account
    from backend.db_controller import DBController
    from AppObjects.category import Category



logger = get_logger(__name__)

class AppCore:
    """Global application state and services. It stores all session variables and methods. Used to load user configuration, app version, and backups."""

    __instance: AppCore|None = None


    def __new__(cls, *args:Any, **kwargs:Any) -> AppCore:
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
            
        return cls.__instance


    def __init__(
            self,
            single_instance_guard:SingleInstanceGuard,
            db_controller:DBController,
            user_config:UserConfig,
            test_mode:bool,
            test_alembic_config:Config|None=None
        ) -> None:
        
        self.app_version = self.load_app_version()

        self.current_month = 4
        self.current_year = 2023
        self.current_balance = 0.0
        self.current_total_income = 0.0
        self.current_total_expenses = 0.0

        self.accounts_list:list[Account] = []
        self.categories:dict[int, Category] = {}
        self.focused_income_category:Category | None
        self.focused_expense_category:Category | None

        self.db = db_controller
        self.backups:dict[str, Backup] = {}

        self.instance_guard = single_instance_guard
        self.test_mode = test_mode

        self.config = user_config
        self.test_alembic_config = test_alembic_config

 
    def start_session(self) -> None:
        """
        Start session. It loads user configuration, app version, and backups.
        It also sets the current date and creates the backups directory if it doesn't exist.
        """

        logger.info("__BREAK_LINE__")
        logger.info("__BREAK_LINE__")
        logger.info("Starting session")
        logger.error("__BREAK_LINE__")
        logger.error("__BREAK_LINE__")
        logger.error(ERROR_LOG_START_MESSAGE)
        sys.excepthook = AppCore.custom_excepthook

        if self.instance_guard.is_running:
            print("Another instance is already running. Exiting.")
            logger.info("Ending session")
            sys.exit(0)
        
        logger.debug(f"App version: {self.app_version}")
            
        #Set current date
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        logger.debug(f"Current month: {self.current_month}, current year: {self.current_year}")
        
        if not os.path.exists(USER_CONF_PATH):
            self.config.create_user_config()
            logger.info("User configuration file created")

        self.config.load_user_config()
        logger.info("User configuration loaded")

        if self.test_mode:
            os.makedirs(TEST_BACKUPS_DIRECTORY, exist_ok=True)
        else:
            os.makedirs(BACKUPS_DIRECTORY, exist_ok=True)
        logger.info("Backups directory created")

        if not os.path.exists(APP_HASHES_DIRECTORY):
            os.makedirs(APP_HASHES_DIRECTORY)
            logger.info("App hashes directory created")

        if not os.path.exists(CACHE_DIRECTORY):
            os.makedirs(CACHE_DIRECTORY)
            logger.info("Cache directory created")
            
        self.load_backups()
        logger.info("Backups loaded")
        logger.info("__BREAK_LINE__")
    

    @staticmethod
    def load_app_version() -> str:
        """Load app version from file as string."""

        with open(os.path.join(APP_DIRECTORY, VERSION_FILE_NAME)) as file:
            app_version = file.read().strip()
        return app_version

        
    def load_backups(self) -> None:
        """Load backups from the backups directory. It loads all backups and adds them to the session."""

        for backup_path in os.listdir(BACKUPS_DIRECTORY) if not self.test_mode else os.listdir(TEST_BACKUPS_DIRECTORY):
            if self.test_mode:
                backup = Backup.parse_db_file_path(os.path.join(TEST_BACKUPS_DIRECTORY, backup_path))
            else:
                backup = Backup.parse_db_file_path(os.path.join(BACKUPS_DIRECTORY, backup_path))
            self.backups[str(id(backup))] = backup
            logger.debug(f"Backup loaded: {backup.db_file_path}")


    def end_session(self) -> None:
        """End session. It closes the database connection, removes the instance guard, and closes all sockets."""

        self.instance_guard.close_sockets()
        self.db.close_connection()
        logger.info("Ending session")
    

    @staticmethod
    def instance() -> AppCore:
        """Get the instance of the AppCore class."""

        if not AppCore.__instance:
            raise RuntimeError("AppCore instance is not created. Call AppCore() to create it.")
        return AppCore.__instance

    @staticmethod
    def custom_excepthook(exc_type:type[BaseException], exc_value:BaseException, exc_traceback:TracebackType | None) -> None:
        """Custom excepthook. It logs the exception to Error log."""

        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        logger.info(f"Ending session with critical error (see {ERROR_LOG_FILE})\n\n")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    
    def restart_app(self) -> None:
        """Restart the app. It closes the current session and starts a new one."""

        self.end_session()
        if DEVELOPMENT_MODE:
            QProcess.startDetached(sys.executable, sys.argv)#First argument using IDE is the path to the script that have to be run 
        else:
            QProcess.startDetached(sys.executable, sys.argv[1:])#First argument in argv is the path to the executable, the second is the list of arguments
        QApplication.quit()
        