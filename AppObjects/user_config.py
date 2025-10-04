from __future__ import annotations
from typing import TYPE_CHECKING
import toml
from enum import Enum

from project_configuration import USER_CONF_PATH, TEST_USER_CONF_PATH, MAX_RECOMMENDED_BACKUPS,\
MAX_RECOMMENDED_LEGACY_BACKUPS

if TYPE_CHECKING:
    UserConfCategory = dict[str, str | int | bool]
    UserConfType = dict[str, UserConfCategory]
    LegacyUserConfType = dict[str, str | int | bool]



class UserConfig:
    """Configuration class. It stores all values that are saved to user configuration file."""

    class AutoBackupStatus(Enum):
        """Auto backup status class. It stores all auto backup statuses."""

        MONTHLY = "monthly"
        WEEKLY = "weekly"
        DAILY = "daily"
        NO_AUTO_BACKUP = "no auto backup"


    class UpdateChannel(Enum):
        """Update channel class. It stores all update channels."""

        RELEASE = "release"
        PRE_RELEASE = "prerelease"


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
        self.update_channel:str = UserConfig.UpdateChannel.RELEASE.value

        self.shortcuts = {
            UserConfig.ShortcutId.CLOSE_CURRENT_WINDOW:"X",
            UserConfig.ShortcutId.OPEN_SETTINGS:"S",
            UserConfig.ShortcutId.OPEN_STATISTICS:"A",
            UserConfig.ShortcutId.SWITCH_ACCOUNT:"Shift+S",
            UserConfig.ShortcutId.SWITCH_TO_INCOME:"Q",
            UserConfig.ShortcutId.SWITCH_TO_EXPENSE:"W",
            UserConfig.ShortcutId.LOAD_PREVIOUS_MONTH:"Shift+Q",
            UserConfig.ShortcutId.LOAD_NEXT_MONTH:"Shift+W",
            UserConfig.ShortcutId.FOCUS_ON_NEXT_CATEGORY:"Ctrl+Right",
            UserConfig.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY:"Ctrl+Left",
            UserConfig.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY:"E",
            UserConfig.ShortcutId.SELECT_PREVIOUS_TRANSACTION:"Up",
            UserConfig.ShortcutId.SELECT_NEXT_TRANSACTION:"Down",
            UserConfig.ShortcutId.DELETE_TRANSACTION:"D",
            UserConfig.ShortcutId.EDIT_TRANSACTION:"C"
        }


    def load_user_config(self) -> None:
        """Load user configuration. It reads the configuration from the file and sets it to the session variables."""

        if self.test_mode:
            with open(TEST_USER_CONF_PATH, encoding="utf-8") as file:
                User_conf:UserConfType = toml.load(file)
        else:
            with open(USER_CONF_PATH, encoding="utf-8") as file:
                User_conf:UserConfType = toml.load(file)#type: ignore[no-redef] #Since type is specified twice, mypy thinks that it is redefined

        if "General" in User_conf: 
            self.theme = str(User_conf["General"].get("Theme", "Dark"))
            self.language = str(User_conf["General"].get("Language", "English"))
            self.account_name = str(User_conf["General"].get("Account_name", ""))
            self.update_channel = str(User_conf["General"].get("Update_channel", UserConfig.UpdateChannel.RELEASE.value))

            self.auto_backup_status = str(User_conf["Backup"].get(
                "Auto_backup_status", UserConfig.AutoBackupStatus.MONTHLY.value)
            )
            self.max_backups = int(User_conf["Backup"].get("Max_backups", self.max_backups))
            self.max_legacy_backups = int(User_conf["Backup"].get("Max_legacy_backups", self.max_legacy_backups))
            self.auto_backup_removal_enabled = bool(User_conf["Backup"].get(
                "Auto_backup_removal_enabled", self.auto_backup_removal_enabled)
            )

            for shortcut_id, shortcut_value in self.shortcuts.items():
                if shortcut_id in User_conf["Shortcuts"]:
                    self.shortcuts[shortcut_id] = str(User_conf["Shortcuts"].get(shortcut_id, shortcut_value))
                else:
                    self.shortcuts[shortcut_id] = shortcut_value

        else:
            # If the file is not in the new format, load it as a legacy configuration (1.1.1)
            Legacy_user_conf:LegacyUserConfType = User_conf # type: ignore #Conflicts with new UserConfType
            self.theme = str(Legacy_user_conf.get("Theme", self.theme))
            self.language = str(Legacy_user_conf.get("Language", self.language))
            self.account_name = str(Legacy_user_conf.get("Account_name", self.account_name))
            self.auto_backup_status = str(Legacy_user_conf.get("Auto_backup_status", self.auto_backup_status))
            self.max_backups = int(Legacy_user_conf.get("Max_backups", self.max_backups))
            self.max_legacy_backups = int(Legacy_user_conf.get("Max_legacy_backups", self.max_legacy_backups))
            self.auto_backup_removal_enabled = bool(Legacy_user_conf.get(
                "Auto_backup_removal_enabled", self.auto_backup_removal_enabled)
            )


    def create_user_config(self) -> None:
        """Create user configuration file. It creates a new file with default values if the file doesn't exist."""

        default_user_configuration = {
            "General":{
                "Theme":"Dark",
                "Language":"English",
                "Account_name":"",
                "Update_channel":UserConfig.UpdateChannel.RELEASE.value
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
                "Account_name":self.account_name,
                "Update_channel":self.update_channel
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
    