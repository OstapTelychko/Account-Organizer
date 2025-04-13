from pathlib import Path

APP_NAME = "Account Organizer"
APP_HOST = "127.0.0.1"
APP_PORT = 6957

REPOSITORY = "Account-Organizer"
REPOSITORY_OWNER = "OstapTelychko"
LATEST_RELEASE_URL = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{REPOSITORY}/releases/latest"

APP_DIRECTORY = __file__.replace("\\","/").replace(Path(__file__).name,"")#The first replace change windows \ to / second replace remove name of file to get path to directory
if APP_DIRECTORY.find("_internal")  == -1:
    ROOT_DIRECTORY = APP_DIRECTORY
    DEVELOPMENT_MODE = True
else:
    ROOT_DIRECTORY = APP_DIRECTORY.replace("/_internal","")
    DEVELOPMENT_MODE = False

IMAGES_DIRECTORY = f"{APP_DIRECTORY}Images/"
FLAGS_DIRECTORY = f"{IMAGES_DIRECTORY}Flags/"
TRANSACTIONS_DIRECTORY = f"{IMAGES_DIRECTORY}Transactions/"
THEME_DIRECTORY = f"{IMAGES_DIRECTORY}Theme/"
GENERAL_ICONS_DIRECTORY = f"{IMAGES_DIRECTORY}General Icons/"
    
USER_CONF_PATH = f"{APP_DIRECTORY}/User_configuration.toml"
TEST_USER_CONF_PATH = f"{APP_DIRECTORY}/test_User_configuration.toml"
DB_PATH = f"sqlite:///{APP_DIRECTORY}Accounts.sqlite"
DB_FILE_PATH = DB_PATH.replace("sqlite:///","")
TEST_DB_PATH = f"sqlite:///{APP_DIRECTORY}test_Accounts.sqlite"
TEST_DB_FILE_PATH = TEST_DB_PATH.replace("sqlite:///","")

UPDATE_DIRECTORY = f"{ROOT_DIRECTORY}Temp Update"
PREVIOUS_VERSION_COPY_DIRECTORY = f"{ROOT_DIRECTORY}Previous Version"
GUI_LIBRARY = "PySide6"
LINUX_UPDATE_ZIP = "linux_update.zip"
WINDOWS_UPDATE_ZIP = "windows_update.zip"
VERSION_FILE_NAME = "app version.txt"
ALEMBIC_CONFIG_FILE = "alembic.ini"
MOVE_FILES_TO_UPDATE = (DB_FILE_PATH, USER_CONF_PATH)

LOGS_DIRECTORY = f"{ROOT_DIRECTORY}Logs/"
APP_LOG_FILE = f"{LOGS_DIRECTORY}App.log"
ERROR_LOG_FILE = f"{LOGS_DIRECTORY}Error.log"
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
BACKUPS_DIRECTORY = f"{ROOT_DIRECTORY}{BACKUPS_DIRECTORY_NAME}"
TEST_BACKUPS_DIRECTORY = f"{ROOT_DIRECTORY}Test DB Backups"
MIN_RECOMMENDED_BACKUPS = 2
MAX_RECOMMENDED_BACKUPS = 15
MIN_RECOMMENDED_LEGACY_BACKUPS = 2
MAX_RECOMMENDED_LEGACY_BACKUPS = 5
BACKUPS_DATE_FORMAT = "%d-%m-%Y_%H-%M-%S"

CATEGORY_TYPE = {0:"Incomes",1:"Expenses"}
FORBIDDEN_CALCULATOR_WORDS = ["import","def","for","while","open","del","__","with","exit","raise","print","range","quit","class","try","if","input","object","global","lambda","match"]
MONTHS_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
AVAILABLE_LANGUAGES = ["English","Українська","Polski"]

MIN_TRANSACTION_VALUE = 0.0
MAX_TRANSACTION_VALUE = 2_000_000_000#2 billion

QCALENDAR_DATE_FORMAT = "dd/MM/yyyy"
MAX_BACKUPS_VALIDATOR_REGEX = r"^[1-9][0-9]{0,2}|1000$"
MAX_LEGACY_BACKUPS_VALIDATOR_REGEX = r"^(?:[1-9]|[1-9]\d|100)$"
TRANSACTION_DAY_REGEX = r"^([1-9]|[12][0-9]|3[01])$"
