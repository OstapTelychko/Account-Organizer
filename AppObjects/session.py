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
    """Session class main app support object. It stores all session variables and methods. Used to load user configuration, app version, and backups."""


    class AutoBackupStatus(Enum):
        """Auto backup status class. It stores all auto backup statuses."""

        MONTHLY = "monthly"
        WEEKLY = "weekly"
        DAILY = "daily"
        NO_AUTO_BACKUP = "no auto backup"
    

    class ShortcutId:
        """Shortcut ID class. It stores all shortcut names, that are used in the app."""

        CLOSE_CURRENT_WINDOW = "Close_current_window"
        OPEN_SETTINGS = "Open_settings"
        OPEN_STATISTICS = "Open_statistics"
        SWITCH_ACCOUNT = "Switch_account"
        SWITCH_TO_INCOME = "Switch_to_income"
        SWITCH_TO_EXPENSE = "Switch_to_expense"
        LOAD_PREVIOUS_MONTH = "Load_previous_month"
        LOAD_NEXT_MONTH = "Load_next_month"
        FOCUS_ON_NEXT_CATEGORY = "Focus_on_next_category"
        FOCUS_ON_PREVIOUS_CATEGORY = "Focus_on_previous_category"
        ADD_TRANSACTION_TO_FOCUSED_CATEGORY = "Add_transaction_to_focused_category"
        SELECT_PREVIOUS_TRANSACTION = "Select_previous_transaction"
        SELECT_NEXT_TRANSACTION = "Select_next_transaction"
        DELETE_TRANSACTION = "Delete_transaction"
        EDIT_TRANSACTION = "Edit_transaction"


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

    language = "Українська"
    theme = "Dark"
    account_name = ""

    db:DBController
    backups:dict[str, Backup] = {}
    auto_backup_status:AutoBackupStatus = AutoBackupStatus.MONTHLY
    auto_backup_removal_enabled:bool = True
    max_backups = MAX_RECOMMENDED_BACKUPS
    max_legacy_backups = MAX_RECOMMENDED_LEGACY_BACKUPS

    instance_guard:SingleInstanceGuard
    test_mode = False
    test_alembic_config:Config

    shortcuts = {
        ShortcutId.CLOSE_CURRENT_WINDOW:"x",
        ShortcutId.OPEN_SETTINGS:"s",
        ShortcutId.OPEN_STATISTICS:"a",
        ShortcutId.SWITCH_ACCOUNT:"shift+s",
        ShortcutId.SWITCH_TO_INCOME:"q",
        ShortcutId.SWITCH_TO_EXPENSE:"w",
        ShortcutId.LOAD_PREVIOUS_MONTH:"shift+q",
        ShortcutId.LOAD_NEXT_MONTH:"shift+w",
        ShortcutId.FOCUS_ON_NEXT_CATEGORY:"ctrl+right",
        ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY:"ctrl+left",
        ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY:"e",
        ShortcutId.SELECT_PREVIOUS_TRANSACTION:"up",
        ShortcutId.SELECT_NEXT_TRANSACTION:"down",
        ShortcutId.DELETE_TRANSACTION:"d",
        ShortcutId.EDIT_TRANSACTION:"c"
    }


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
        
        if not os.path.exists(USER_CONF_PATH):
            Session.create_user_config()
            logger.info("User configuration file created")

        Session.load_user_config()
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
    def load_user_config():
        """Load user configuration. It reads the configuration from the file and sets it to the session variables."""

        if Session.test_mode:
            with open(TEST_USER_CONF_PATH) as file:
                User_conf = toml.load(file)
        else:
            with open(USER_CONF_PATH) as file:
                User_conf = toml.load(file)

        if "General" in User_conf: 
            Session.theme = User_conf["General"].get("Theme", "Dark")
            Session.language = User_conf["General"].get("Language", "English")
            Session.account_name = User_conf["General"].get("Account_name", "")

            Session.auto_backup_status = User_conf["Backup"].get("Auto_backup_status", Session.AutoBackupStatus.MONTHLY.value)
            Session.max_backups = User_conf["Backup"].get("Max_backups", MAX_RECOMMENDED_BACKUPS)
            Session.max_legacy_backups = User_conf["Backup"].get("Max_legacy_backups", MAX_RECOMMENDED_LEGACY_BACKUPS)
            Session.auto_backup_removal_enabled = User_conf["Backup"].get("Auto_backup_removal_enabled", True)

            Session.shortcuts[Session.ShortcutId.CLOSE_CURRENT_WINDOW] = User_conf["Shortcuts"].get("Close_current_window", Session.shortcuts[Session.ShortcutId.CLOSE_CURRENT_WINDOW])
            Session.shortcuts[Session.ShortcutId.OPEN_SETTINGS] = User_conf["Shortcuts"].get("Open_settings", Session.shortcuts[Session.ShortcutId.OPEN_SETTINGS])
            Session.shortcuts[Session.ShortcutId.OPEN_STATISTICS] = User_conf["Shortcuts"].get("Open_statistics", Session.shortcuts[Session.ShortcutId.OPEN_STATISTICS])
            Session.shortcuts[Session.ShortcutId.SWITCH_ACCOUNT] = User_conf["Shortcuts"].get("Switch_account", Session.shortcuts[Session.ShortcutId.SWITCH_ACCOUNT])
            Session.shortcuts[Session.ShortcutId.SWITCH_TO_INCOME] = User_conf["Shortcuts"].get("Switch_to_income", Session.shortcuts[Session.ShortcutId.SWITCH_TO_INCOME])
            Session.shortcuts[Session.ShortcutId.SWITCH_TO_EXPENSE] = User_conf["Shortcuts"].get("Switch_to_expense", Session.shortcuts[Session.ShortcutId.SWITCH_TO_EXPENSE])
            Session.shortcuts[Session.ShortcutId.SELECT_PREVIOUS_TRANSACTION] = User_conf["Shortcuts"].get("Select_previous_transaction", Session.shortcuts[Session.ShortcutId.SELECT_PREVIOUS_TRANSACTION])
            Session.shortcuts[Session.ShortcutId.SELECT_NEXT_TRANSACTION] = User_conf["Shortcuts"].get("Select_next_transaction", Session.shortcuts[Session.ShortcutId.SELECT_NEXT_TRANSACTION])

        else:
        # If the file is not in the new format, load it as a legacy configuration (1.1.1)
            Session.theme = User_conf.get("Theme", "Dark")
            Session.language = User_conf.get("Language", "English")
            Session.account_name = User_conf.get("Account_name", "")
            Session.auto_backup_status = User_conf.get("Auto_backup_status", Session.AutoBackupStatus.MONTHLY.value)
            Session.max_backups = User_conf.get("Max_backups", MAX_RECOMMENDED_BACKUPS)
            Session.max_legacy_backups = User_conf.get("Max_legacy_backups", MAX_RECOMMENDED_LEGACY_BACKUPS)
            Session.auto_backup_removal_enabled = User_conf.get("Auto_backup_removal_enabled", True)


    @staticmethod
    def create_user_config():
        """Create user configuration file. It creates a new file with default values if the file doesn't exist."""

        default_user_configuration = {
            "General":{
                "Theme":"Dark",
                "Language":"English",
                "Account_name":"",
            },
            "Backup":{
                "Auto_backup_status":Session.AutoBackupStatus.MONTHLY.value,
                "Max_backups":MAX_RECOMMENDED_BACKUPS,
                "Max_legacy_backups":MAX_RECOMMENDED_LEGACY_BACKUPS,
                "Auto_backup_removal_enabled":True
            },
            "Shortcuts":{
                **Session.shortcuts,
            }
        }

        if Session.test_mode:
            with open(TEST_USER_CONF_PATH, "w", encoding="utf-8") as file:
                toml.dump(default_user_configuration, file)
        else:   
            with open(USER_CONF_PATH, "w", encoding="utf-8") as file:
                toml.dump(default_user_configuration, file)

        
    @staticmethod    
    def update_user_config():
        """Update user configuration file. It updates the file with the current values of the session variables."""

        user_config = {
            "General":{
                "Theme":Session.theme,
                "Language":Session.language,
                "Account_name":Session.account_name
            },
            "Backup":{
                "Auto_backup_status":Session.auto_backup_status,
                "Max_backups":Session.max_backups,
                "Max_legacy_backups":Session.max_legacy_backups,
                "Auto_backup_removal_enabled":Session.auto_backup_removal_enabled
            },
            "Shortcuts":{
                **Session.shortcuts
            }
        }

        if Session.test_mode:
            with open(TEST_USER_CONF_PATH, "w", encoding="utf-8") as file:
                toml.dump(user_config, file)
        else:
            with open(USER_CONF_PATH, "w", encoding="utf-8") as file:
                toml.dump(user_config, file)
    

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
        