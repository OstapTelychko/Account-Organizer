from Session import Session
from GUI import MainWindow
from languages import LANGUAGES
from AppManagement.category import load_categories_data


def next_month():
    if Session.current_month != 12:
        Session.current_month +=1
        MainWindow.current_month.setText(LANGUAGES[Session.language]["Months"][Session.current_month])
    else:
        MainWindow.current_month.setText(LANGUAGES[Session.language]["Months"][1])
        Session.current_month = 1
    load_categories_data()


def previous_month():
    Session.current_month -= 1
    if Session.current_month != 0:
        MainWindow.current_month.setText(LANGUAGES[Session.language]["Months"][Session.current_month])
    else:
        MainWindow.current_month.setText(LANGUAGES[Session.language]["Months"][12])
        Session.current_month = 12
    load_categories_data()


def next_year():
    Session.current_year += 1
    MainWindow.current_year.setText(str(Session.current_year))
    load_categories_data()


def previous_year():
    Session.current_year -= 1
    MainWindow.current_year.setText(str(Session.current_year))
    load_categories_data()