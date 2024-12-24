from pathlib import Path

APP_NAME = "Account Organizer"
APP_HOST = "127.0.0.1"
APP_PORT = 6957

APP_DIRECTORY = __file__.replace("\\","/").replace(Path(__file__).name,"")#The first replace change windows \ to / second replace remove name of file to get path to directory
if APP_DIRECTORY.find("_internal")  == -1:
    ROOT_DIRECTORY = APP_DIRECTORY
else:
    ROOT_DIRECTORY = APP_DIRECTORY.replace("/_internal","")
    
BACKUPS_DIRECTORY = f"{ROOT_DIRECTORY}DB Backups"
MIN_RECOMMENDED_BACKUPS = 2
MAX_RECOMMENDED_BACKUPS = 15

USER_CONF_PATH = f"{APP_DIRECTORY}/User_configuration.toml"
DB_PATH = f"sqlite:///{APP_DIRECTORY}Accounts.sqlite"
DB_FILE_PATH = DB_PATH.replace("sqlite:///","")
TEST_DB_PATH = f"sqlite:///{APP_DIRECTORY}test_Accounts.sqlite"
TEST_DB_FILE_PATH = TEST_DB_PATH.replace("sqlite:///","")

CATEGORY_TYPE = {0:"Incomes",1:"Expenses"}
FORBIDDEN_CALCULATOR_WORDS = ["import","def","for","while","open","del","__","with","exit","raise","print","range","quit","class","try","if","input","object","global","lambda","match"]
MONTHS_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
AVAILABLE_LANGUAGES = ["English","Українська","Polski"]
