from datetime import datetime
import toml

from project_configuration import ROOT_DIRECTORY
from Account import Account



class Session:
    Current_month = 1
    Current_year = 2023

    Current_balance = 0
    Current_total_income = 0
    Current_total_expenses = 0

    Accounts_list = []
    Categories = {}

    Switch_account = True

    Language = "Українська"
    Theme = "Dark"
    Account_name = ""

    account:Account = None#I added  :Account to allow my IDE to highlight the functions of Account class


    def start_session():
        Session.Current_month = datetime.now().month
        Session.Current_year = datetime.now().year

        with open(f"{ROOT_DIRECTORY}/User_configuration.toml") as file:
            User_conf = toml.load(f"{ROOT_DIRECTORY}/User_configuration.toml")

            #Load selected language 
            Session.Language = User_conf["Language"]
            Session.Theme = User_conf["Theme"]
            #Load last used account name 
            Session.Account_name = User_conf["Account_name"]

        
    

    def update_user_config():
        with open(f"{ROOT_DIRECTORY}/User_configuration.toml","w",encoding="utf-8") as file:
            toml.dump({"Theme":Session.Theme, "Language":Session.Language, "Account_name":Session.Account_name},file)
    