import toml
import os
from sys import exit
from datetime import datetime
from alembic.config import Config

from project_configuration import USER_CONF_PATH, APP_DIRECTORY, BACKUPS_DIRECTORY, TEST_BACKUPS_DIRECTORY, MAX_RECOMMENDED_BACKUPS, MAX_RECOMMENDED_LEGACY_BACKUPS
from backend.db_controller import DBController
from AppObjects.single_instance_guard import SingleInstanceGuard
from AppObjects.category import Category
from AppObjects.backup import Backup




class Session:

    class AutoBackupStatus:
        MONTHLY = "monthly"
        WEEKLY = "weekly"
        DAILY = "daily"
        NO_AUTO_BACKUP = "no auto backup"
    

    app_version:str = None

    current_month = 4
    current_year = 2023
    current_balance = 0
    current_total_income = 0
    current_total_expenses = 0

    accounts_list = []
    categories:dict[int, Category] = {}

    switch_account = True

    language = "Українська"
    theme = "Dark"
    account_name = ""

    db:DBController = None
    backups:dict[int, Backup] = {}
    auto_backup_status:AutoBackupStatus = AutoBackupStatus.MONTHLY
    auto_backup_removal_enabled:bool = True
    max_backups = MAX_RECOMMENDED_BACKUPS
    max_legacy_backups = MAX_RECOMMENDED_LEGACY_BACKUPS

    instance_guard:SingleInstanceGuard = None
    test_mode = False
    test_alembic_config:Config = None


    def start_session():
        Session.instance_guard = SingleInstanceGuard()

        if Session.instance_guard.is_running:
            print("Another instance is already running. Exiting.")
            exit(0)
        
        Session.load_app_version()
            
        #Set current date
        Session.current_month = datetime.now().month
        Session.current_year = datetime.now().year
        
        if not os.path.exists(USER_CONF_PATH):
            Session.create_user_config()

        Session.load_user_config()
        if Session.test_mode:
            os.makedirs(TEST_BACKUPS_DIRECTORY, exist_ok=True)
        else:
            os.makedirs(BACKUPS_DIRECTORY, exist_ok=True)
        Session.load_backups()
    

    def load_app_version():
        with open(f"{APP_DIRECTORY}/app version.txt") as file:
            Session.app_version = file.read().strip()


    def load_user_config():
        with open(USER_CONF_PATH) as file:
            User_conf = toml.load(USER_CONF_PATH)

            Session.theme = User_conf.get("Theme", "Dark")
            Session.language = User_conf.get("Language", "English")
            Session.account_name = User_conf.get("Account_name", "")
            Session.auto_backup_status = User_conf.get("Auto_backup_status", Session.AutoBackupStatus.MONTHLY)
            Session.max_backups = User_conf.get("Max_backups", MAX_RECOMMENDED_BACKUPS)
            Session.max_legacy_backups = User_conf.get("Max_legacy_backups", MAX_RECOMMENDED_LEGACY_BACKUPS)
            Session.auto_backup_removal_enabled = User_conf.get("Auto_backup_removal_enabled", True)


    def create_user_config():
        default_user_configuration = {
            "Theme":"Dark",
            "Language":"English",
            "Account_name":"",
            "Auto_backup_status":Session.AutoBackupStatus.MONTHLY,
            "Max_backups":MAX_RECOMMENDED_BACKUPS,
            "Max_legacy_backups":MAX_RECOMMENDED_LEGACY_BACKUPS,
            "Auto_backup_removal_enabled":True
        }

        with open(USER_CONF_PATH, "w", encoding="utf-8") as file:
            toml.dump(default_user_configuration, file)

        
    def update_user_config():
        with open(USER_CONF_PATH, "w", encoding="utf-8") as file:
            toml.dump({
                "Theme":Session.theme,
                "Language":Session.language,
                "Account_name":Session.account_name,
                "Auto_backup_status":Session.auto_backup_status,
                "Max_backups":Session.max_backups,
                "Max_legacy_backups":Session.max_legacy_backups,
                "Auto_backup_removal_enabled":Session.auto_backup_removal_enabled
            }, file)
    

    def load_backups():
        for backup in os.listdir(BACKUPS_DIRECTORY) if not Session.test_mode else os.listdir(TEST_BACKUPS_DIRECTORY):
            if Session.test_mode:
                backup = Backup.parse_db_file_path(os.path.join(TEST_BACKUPS_DIRECTORY, backup))
            else:
                backup = Backup.parse_db_file_path(os.path.join(BACKUPS_DIRECTORY, backup))
            Session.backups[str(id(backup))] = backup
