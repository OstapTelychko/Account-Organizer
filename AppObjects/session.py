import toml
import os
from sys import exit
from datetime import datetime

from project_configuration import USER_CONF_PATH
from backend.db_controller import DBController
from AppObjects.single_instance_guard import SingleInstanceGuard
from AppObjects.category import Category



class Session:
    current_month = 1
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
    instance_guard:SingleInstanceGuard = None
    test_mode = False


    def start_session():
        Session.instance_guard = SingleInstanceGuard()

        if Session.instance_guard.is_running:
            print("Another instance is already running. Exiting.")
            exit(0)
            
        #Set current date
        Session.current_month = datetime.now().month
        Session.current_year = datetime.now().year
        
        if not os.path.exists(USER_CONF_PATH):
            Session.create_user_config()

        Session.load_user_config()
    

    def load_user_config():
        with open(USER_CONF_PATH) as file:
            User_conf = toml.load(USER_CONF_PATH)

            #Load selected language 
            Session.language = User_conf["Language"]
            Session.theme = User_conf["Theme"]
            #Load last used account name 
            Session.account_name = User_conf["Account_name"]


    def create_user_config():
        default_user_configuration = {
            "Theme":"Dark",
            "Language":"English",
            "Account_name":""
        }

        with open(USER_CONF_PATH, "w", encoding="utf-8") as file:
            toml.dump(default_user_configuration, file)

        
    def update_user_config():
        with open(USER_CONF_PATH, "w", encoding="utf-8") as file:
            toml.dump({"Theme":Session.theme, "Language":Session.language, "Account_name":Session.account_name}, file)
    