from GUI import *
from Languages import LANGUAGES
from datetime import datetime
import toml


Current_balance = 0
Current_month = datetime.now().month
Current_year = datetime.now().year

def update_config():
    with open("./configuration.toml","w",encoding="utf-8") as file:
        toml.dump(Configuration,file)


def swith_theme():
    global Configuration
    if Configuration["Theme"] == "Dark":
        app.setStyleSheet(light_theme)
        Settings_window.switch_themes_button.setIcon(light_theme_icon)
        Configuration.update({"Theme" : "Light"})
    elif Configuration["Theme"] == "Light":
        app.setStyleSheet(dark_theme)
        Settings_window.switch_themes_button.setIcon(dark_theme_icon)
        Configuration.update({"Theme" : "Dark"})
    update_config()

def change_language(language):
    global Configuration,Language

    if type(language) is int:
        language = [*LANGUAGES.keys()][language]
        Configuration["Language"] = language
        Language = language
    else:
        Configuration["Language"] = language
        Language = language
    update_config()

    Main_window.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(Current_balance))
    Main_window.current_month.setText(LANGUAGES[Language]["Months"][Current_month])


def next_month():
    global Current_month

    if Current_month != 12:
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][Current_month+1])
        Current_month +=1
    else:
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][1])
        Current_month = 1


def previous_month():
    global Current_month

    Current_month -= 1
    if Current_month != 0:
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][Current_month])
    else:
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][12])
        Current_month = 12


def next_year():
    global Current_year

    Current_year += 1
    Main_window.current_year.setText(str(Current_year))


def previous_year():
    global Current_year

    Current_year -= 1
    Main_window.current_year.setText(str(Current_year))



if __name__ == "__main__":
    with open("./configuration.toml") as file:
        Configuration = toml.load("./configuration.toml")
    #Load selected language 
    Language = Configuration["Language"]
    change_language(Language)
    Settings_window.languages.setCurrentIndex([*LANGUAGES.keys()].index(Language))

    #Set selected theme
    if Configuration["Theme"] == "Dark":
        app.setStyleSheet(dark_theme)
        Settings_window.switch_themes_button.setIcon(dark_theme_icon)
    if Configuration["Theme"] == "Light":
        app.setStyleSheet(light_theme)
        Settings_window.switch_themes_button.setIcon(light_theme_icon)

    #Set current month and year
    Main_window.current_year.setText(str(Current_year))
    Main_window.current_month.setText(LANGUAGES[Language]["Months"][Current_month])

    #Connect buttons to functions
    Main_window.settings.clicked.connect(Settings_window.window.exec)
    Settings_window.switch_themes_button.clicked.connect(swith_theme)
    Settings_window.languages.currentIndexChanged.connect(change_language)
    Main_window.next_month_button.clicked.connect(next_month)
    Main_window.previous_month_button.clicked.connect(previous_month)
    Main_window.next_year_button.clicked.connect(next_year)
    Main_window.previous_year_button.clicked.connect(previous_year)
    Main_window.window.show()
    app.exec()