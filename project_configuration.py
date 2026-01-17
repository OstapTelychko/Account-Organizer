import os
from pathlib import Path
from sys import platform

APP_NAME = "Account Organizer"
APP_HOST = "127.0.0.1"
APP_PORT = 6957

REPOSITORY = "Account-Organizer"
REPOSITORY_OWNER = "OstapTelychko"
RELEASES_URL = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{REPOSITORY}/releases"
LATEST_RELEASE_URL = f"{RELEASES_URL}/latest"

APP_DIRECTORY = __file__.replace("\\","/").replace(Path(__file__).name,"")#The first replace change windows \ to / second replace remove name of file to get path to directory
if APP_DIRECTORY.find("_internal")  == -1:
    ROOT_DIRECTORY = APP_DIRECTORY
    DEVELOPMENT_MODE = True
else:
    ROOT_DIRECTORY = APP_DIRECTORY.replace("/_internal","")
    DEVELOPMENT_MODE = False
DEVELOPMENT_ROOT_DIRECTORY = os.path.join(ROOT_DIRECTORY, "dist", "main")

if platform == "win32":
    MAIN_EXECUTABLE = "main.exe"
else:
    MAIN_EXECUTABLE = "main"

IMAGES_DIRECTORY = os.path.join(APP_DIRECTORY, "Images")
FLAGS_DIRECTORY = os.path.join(IMAGES_DIRECTORY, "Flags")
TRANSACTIONS_DIRECTORY = os.path.join(IMAGES_DIRECTORY, "Transactions")
THEME_DIRECTORY = os.path.join(IMAGES_DIRECTORY, "Theme")
GENERAL_ICONS_DIRECTORY = os.path.join(IMAGES_DIRECTORY, "General Icons")

USER_CONF_PATH = os.path.join(APP_DIRECTORY, "User_configuration.toml")
TEST_USER_CONF_PATH = os.path.join(APP_DIRECTORY, "test_User_configuration.toml")
DB_PATH = f"sqlite:///{APP_DIRECTORY}Accounts.sqlite"
DB_FILE_PATH = DB_PATH.replace("sqlite:///","")
TEST_DB_PATH = f"sqlite:///{APP_DIRECTORY}test_Accounts.sqlite"
TEST_DB_FILE_PATH = TEST_DB_PATH.replace("sqlite:///","")

GUI_LIBRARY = "PySide6"
GUI_LIBRARY_DIRECTORY = os.path.join(APP_DIRECTORY, GUI_LIBRARY)
DEVELOPMENT_GUI_LIBRARY_DIRECTORY = os.path.join(DEVELOPMENT_ROOT_DIRECTORY, "_internal", GUI_LIBRARY)
GUI_LIBRARY_ZIP = f"{GUI_LIBRARY}.zip"

APP_HASHES_DIRECTORY_NAME = "App Hashes"
APP_HASHES_DIRECTORY = os.path.join(APP_DIRECTORY, APP_HASHES_DIRECTORY_NAME)
TEST_APP_HASHES_DIRECTORY = os.path.join(APP_DIRECTORY, "Test App Hashes")
GUI_LIBRARY_HASH_FILE = f"{GUI_LIBRARY}.hash256"
GUI_LIBRARY_HASH_FILE_PATH = os.path.join(APP_HASHES_DIRECTORY, GUI_LIBRARY_HASH_FILE)
TEST_GUI_LIBRARY_HASH_FILE_PATH = os.path.join(TEST_APP_HASHES_DIRECTORY, GUI_LIBRARY_HASH_FILE)

CACHE_DIRECTORY = os.path.join(ROOT_DIRECTORY, "Cache")
DARK_THEME_CACHE_FILE = os.path.join(CACHE_DIRECTORY, "dark_theme.txt")
LIGHT_THEME_CACHE_FILE = os.path.join(CACHE_DIRECTORY, "light_theme.txt")

UPDATE_DIRECTORY = os.path.join(ROOT_DIRECTORY, "Temp Update")
TEST_UPDATE_DIRECTORY = os.path.join(APP_DIRECTORY, "Test Temp Update")
UPDATE_APP_DIRECTORY = os.path.join(UPDATE_DIRECTORY, '_internal')
TEST_UPDATE_APP_DIRECTORY = os.path.join(TEST_UPDATE_DIRECTORY, '_internal')
GUI_LIBRARY_UPDATE_PATH = os.path.join(UPDATE_APP_DIRECTORY, GUI_LIBRARY)
PREVIOUS_VERSION_COPY_DIRECTORY = os.path.join(ROOT_DIRECTORY, "Previous Version")
TEST_PREVIOUS_VERSION_COPY_DIRECTORY = os.path.join(TEST_UPDATE_DIRECTORY, "Previous Version")
LINUX_GUI_LIBRARY_ZIP = f"Linux_{GUI_LIBRARY_ZIP}"
WINDOWS_GUI_LIBRARY_ZIP = f"Windows_{GUI_LIBRARY_ZIP}"
MOVE_FILES_TO_UPDATE_INTERNAL = (DB_FILE_PATH, USER_CONF_PATH)#Those files are stored in _internal directory, so they have to be moved separately into new _internal directory
MOVE_DIRECTORIES_TO_UPDATE_INTERNAL = (APP_HASHES_DIRECTORY,)
LINUX_UPDATE_ZIP = "linux_update.zip"
WINDOWS_UPDATE_ZIP = "windows_update.zip"
VERSION_FILE_NAME = "app version.txt"
ALEMBIC_CONFIG_FILE = "alembic.ini"
ATTEMPTS_TO_DOWNLOAD_ZIP = 3

CHUNK_SIZE_FOR_DOWNLOADING = 1024*256#256 KB
CHUNK_SIZE_FOR_FILE_HASHER = 1024*1024*1#1 MB

LOGS_DIRECTORY = os.path.join(ROOT_DIRECTORY, "Logs")
APP_LOG_FILE = os.path.join(LOGS_DIRECTORY, "App.log")
ERROR_LOG_FILE = os.path.join(LOGS_DIRECTORY, "Error.log")
MAX_LOG_SIZE = 5*1024*1024#5 MB
MAX_ERROR_LOG_SIZE = 2*1024*1024#2 MB
MAX_LOG_BACKUPS = 5
APP_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
ERROR_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s"
LOG_DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

ERROR_LOG_START_MESSAGE = "Starting session. I hope you won't see any messages below this line."
TERMINAL_IGNORE_LOG_MESSAGES = {ERROR_LOG_START_MESSAGE}
REPLACE_LOG_MESSAGES = {"__BREAK_LINE__":"",} 

BACKUPS_DIRECTORY_NAME = "DB Backups"
UPDATE_BACKUPS_DIRECTORY = os.path.join(UPDATE_DIRECTORY, BACKUPS_DIRECTORY_NAME)
TEST_UPDATE_BACKUPS_DIRECTORY = os.path.join(TEST_UPDATE_DIRECTORY, BACKUPS_DIRECTORY_NAME)

BACKUPS_DIRECTORY = os.path.join(ROOT_DIRECTORY, BACKUPS_DIRECTORY_NAME)
DEVELOPMENT_BACKUPS_DIRECTORY = os.path.join(DEVELOPMENT_ROOT_DIRECTORY, BACKUPS_DIRECTORY_NAME)
TEST_BACKUPS_DIRECTORY = os.path.join(ROOT_DIRECTORY, "Test DB Backups")

PREVIOUS_VERSION_BACKUPS_DIRECTORY = os.path.join(PREVIOUS_VERSION_COPY_DIRECTORY, BACKUPS_DIRECTORY_NAME)
MIN_RECOMMENDED_BACKUPS = 2
MAX_RECOMMENDED_BACKUPS = 15
MIN_RECOMMENDED_LEGACY_BACKUPS = 2
MAX_RECOMMENDED_LEGACY_BACKUPS = 5
BACKUPS_DATE_FORMAT = "%d-%m-%Y_%H-%M-%S"

FORBIDDEN_CALCULATOR_WORDS = [
    "import","def","for","while","open","del","__",
    "with","exit","raise","print","range","quit","class","try",
    "if","input","object","global","lambda","match"
]
AVAILABLE_LANGUAGES = ["English","Українська","Polski"]

MIN_TRANSACTION_VALUE = 0.0
MAX_TRANSACTION_VALUE = 2_000_000_000#2 billion

QCALENDAR_DATE_FORMAT = "dd/MM/yyyy"
INFORMATION_MESSAGE_DURATION = 500#Milliseconds
INFORMATION_MESSAGE_STEP_INTERVAL = 60 #FPS for animation
INFORMATION_MESSAGE_STEPS = INFORMATION_MESSAGE_DURATION / INFORMATION_MESSAGE_STEP_INTERVAL

MAX_BACKUPS_VALIDATOR_REGEX = r"^[1-9][0-9]{0,2}|1000$"
MAX_LEGACY_BACKUPS_VALIDATOR_REGEX = r"^(?:[1-9]|[1-9]\d|100)$"
TRANSACTION_DAY_REGEX = r"^([1-9]|[12][0-9]|3[01])$"


class CategoryType:
    Income = "Incomes"
    Expense = "Expenses"
    

    @staticmethod
    def get(index: int) -> str:
        if index == 0:
            return CategoryType.Income
        elif index == 1:
            return CategoryType.Expense
        else:
            raise ValueError("Invalid category type index")
    

    @staticmethod
    def get_index(category_type: str) -> int:
        if category_type == CategoryType.Income:
            return 0
        elif category_type == CategoryType.Expense:
            return 1
        else:
            raise ValueError("Invalid category type string")