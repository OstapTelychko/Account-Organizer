from __future__ import annotations
import toml
from enum import Enum

from project_configuration import USER_CONF_PATH, TEST_USER_CONF_PATH, MAX_RECOMMENDED_BACKUPS, MAX_RECOMMENDED_LEGACY_BACKUPS



class UserConfig:
    """Configuration class. It stores all values that are saved to user configuration file."""

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
    

    def __init__(self, test_mode:bool = False) -> None:
        self.test_mode = test_mode

        self.language:str = "Українська"
        self.theme:str = "Dark"
        self.account_name:str = ""
        self.auto_backup_status:str = UserConfig.AutoBackupStatus.MONTHLY.value
        self.max_backups:int = MAX_RECOMMENDED_BACKUPS
        self.max_legacy_backups:int = MAX_RECOMMENDED_LEGACY_BACKUPS
        self.auto_backup_removal_enabled:bool = True

        self.shortcuts = {
            UserConfig.ShortcutId.CLOSE_CURRENT_WINDOW:"x",
            UserConfig.ShortcutId.OPEN_SETTINGS:"s",
            UserConfig.ShortcutId.OPEN_STATISTICS:"a",
            UserConfig.ShortcutId.SWITCH_ACCOUNT:"shift+s",
            UserConfig.ShortcutId.SWITCH_TO_INCOME:"q",
            UserConfig.ShortcutId.SWITCH_TO_EXPENSE:"w",
            UserConfig.ShortcutId.LOAD_PREVIOUS_MONTH:"shift+q",
            UserConfig.ShortcutId.LOAD_NEXT_MONTH:"shift+w",
            UserConfig.ShortcutId.FOCUS_ON_NEXT_CATEGORY:"ctrl+right",
            UserConfig.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY:"ctrl+left",
            UserConfig.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY:"e",
            UserConfig.ShortcutId.SELECT_PREVIOUS_TRANSACTION:"up",
            UserConfig.ShortcutId.SELECT_NEXT_TRANSACTION:"down",
            UserConfig.ShortcutId.DELETE_TRANSACTION:"d",
            UserConfig.ShortcutId.EDIT_TRANSACTION:"c"
        }



    def load_user_config(self) -> None:
        """Load user configuration. It reads the configuration from the file and sets it to the session variables."""

        if self.test_mode:
            with open(TEST_USER_CONF_PATH) as file:
                User_conf = toml.load(file)
        else:
            with open(USER_CONF_PATH) as file:
                User_conf = toml.load(file)

        if "General" in User_conf: 
            self.theme = User_conf["General"].get("Theme", "Dark")
            self.language = User_conf["General"].get("Language", "English")
            self.account_name = User_conf["General"].get("Account_name", "")

            self.auto_backup_status = User_conf["Backup"].get("Auto_backup_status", UserConfig.AutoBackupStatus.MONTHLY.value)
            self.max_backups = User_conf["Backup"].get("Max_backups", self.max_backups)
            self.max_legacy_backups = User_conf["Backup"].get("Max_legacy_backups", self.max_legacy_backups)
            self.auto_backup_removal_enabled = User_conf["Backup"].get("Auto_backup_removal_enabled", self.auto_backup_removal_enabled)

            self.shortcuts[UserConfig.ShortcutId.CLOSE_CURRENT_WINDOW] = User_conf["Shortcuts"].get(
                UserConfig.ShortcutId.CLOSE_CURRENT_WINDOW, self.shortcuts[UserConfig.ShortcutId.CLOSE_CURRENT_WINDOW])
            self.shortcuts[UserConfig.ShortcutId.OPEN_SETTINGS] = User_conf["Shortcuts"].get(
                UserConfig.ShortcutId.OPEN_SETTINGS, self.shortcuts[UserConfig.ShortcutId.OPEN_SETTINGS])
            self.shortcuts[UserConfig.ShortcutId.OPEN_STATISTICS] = User_conf["Shortcuts"].get(
                UserConfig.ShortcutId.OPEN_STATISTICS, self.shortcuts[UserConfig.ShortcutId.OPEN_STATISTICS])
            self.shortcuts[UserConfig.ShortcutId.SWITCH_ACCOUNT] = User_conf["Shortcuts"].get(
                UserConfig.ShortcutId.SWITCH_ACCOUNT, self.shortcuts[UserConfig.ShortcutId.SWITCH_ACCOUNT])
            self.shortcuts[UserConfig.ShortcutId.SWITCH_TO_INCOME] = User_conf["Shortcuts"].get(
                UserConfig.ShortcutId.SWITCH_TO_INCOME, self.shortcuts[UserConfig.ShortcutId.SWITCH_TO_INCOME])
            self.shortcuts[UserConfig.ShortcutId.SWITCH_TO_EXPENSE] = User_conf["Shortcuts"].get(
                UserConfig.ShortcutId.SWITCH_TO_EXPENSE, self.shortcuts[UserConfig.ShortcutId.SWITCH_TO_EXPENSE])
            self.shortcuts[UserConfig.ShortcutId.SELECT_PREVIOUS_TRANSACTION] = User_conf["Shortcuts"].get(
                UserConfig.ShortcutId.SELECT_PREVIOUS_TRANSACTION, self.shortcuts[UserConfig.ShortcutId.SELECT_PREVIOUS_TRANSACTION])
            self.shortcuts[UserConfig.ShortcutId.SELECT_NEXT_TRANSACTION] = User_conf["Shortcuts"].get(
                UserConfig.ShortcutId.SELECT_NEXT_TRANSACTION, self.shortcuts[UserConfig.ShortcutId.SELECT_NEXT_TRANSACTION])

        else:
            # If the file is not in the new format, load it as a legacy configuration (1.1.1)
            self.theme = User_conf.get("Theme", self.theme)
            self.language = User_conf.get("Language", self.language)
            self.account_name = User_conf.get("Account_name", self.account_name)
            self.auto_backup_status = User_conf.get("Auto_backup_status", self.auto_backup_status)
            self.max_backups = User_conf.get("Max_backups", self.max_backups)
            self.max_legacy_backups = User_conf.get("Max_legacy_backups", self.max_legacy_backups)
            self.auto_backup_removal_enabled = User_conf.get("Auto_backup_removal_enabled", self.auto_backup_removal_enabled)
    

    def create_user_config(self) -> None:
        """Create user configuration file. It creates a new file with default values if the file doesn't exist."""

        default_user_configuration = {
            "General":{
                "Theme":"Dark",
                "Language":"English",
                "Account_name":"",
            },
            "Backup":{
                "Auto_backup_status":UserConfig.AutoBackupStatus.MONTHLY.value,
                "Max_backups":MAX_RECOMMENDED_BACKUPS,
                "Max_legacy_backups":MAX_RECOMMENDED_LEGACY_BACKUPS,
                "Auto_backup_removal_enabled":True
            },
            "Shortcuts":{
                **self.shortcuts,
            }
        }

        if self.test_mode:
            with open(TEST_USER_CONF_PATH, "w", encoding="utf-8") as file:
                toml.dump(default_user_configuration, file)
        else:   
            with open(USER_CONF_PATH, "w", encoding="utf-8") as file:
                toml.dump(default_user_configuration, file)


    def update_user_config(self) -> None:
        """Update user configuration file. It updates the file with the current values of the session variables."""

        user_config = {
            "General":{
                "Theme":self.theme,
                "Language":self.language,
                "Account_name":self.account_name
            },
            "Backup":{
                "Auto_backup_status":self.auto_backup_status,
                "Max_backups":self.max_backups,
                "Max_legacy_backups":self.max_legacy_backups,
                "Auto_backup_removal_enabled":self.auto_backup_removal_enabled
            },
            "Shortcuts":{
                **self.shortcuts
            }
        }

        if self.test_mode:
            with open(TEST_USER_CONF_PATH, "w", encoding="utf-8") as file:
                toml.dump(user_config, file)
        else:
            with open(USER_CONF_PATH, "w", encoding="utf-8") as file:
                toml.dump(user_config, file)
    