from datetime import datetime
import toml

from project_configuration import ROOT_DIRECTORY
from Account import Account



class Session:
    current_month = 1
    current_year = 2023

    current_balance = 0
    current_total_income = 0
    current_total_expenses = 0

    accounts_list = []
    categories = {}

    switch_account = True

    language = "Українська"
    theme = "Dark"
    account_name = ""

    account:Account = None#I added  :Account to allow my IDE to highlight the functions of Account class


    def start_session():
        Session.current_month = datetime.now().month
        Session.current_year = datetime.now().year

        with open(f"{ROOT_DIRECTORY}/User_configuration.toml") as file:
            User_conf = toml.load(f"{ROOT_DIRECTORY}/User_configuration.toml")

            #Load selected language 
            Session.language = User_conf["Language"]
            Session.theme = User_conf["Theme"]
            #Load last used account name 
            Session.account_name = User_conf["Account_name"]

        
    def update_user_config():
        with open(f"{ROOT_DIRECTORY}/User_configuration.toml","w",encoding="utf-8") as file:
            toml.dump({"Theme":Session.theme, "Language":Session.language, "Account_name":Session.account_name}, file)
    