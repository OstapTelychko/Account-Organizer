from Session import Session
from GUI import MainWindow
from languages import LANGUAGES
from category_management import load_categories_data


def next_month():
    if Session.Current_month != 12:
        Session.Current_month +=1
        MainWindow.current_month.setText(LANGUAGES[Session.Language]["Months"][Session.Current_month])
    else:
        MainWindow.current_month.setText(LANGUAGES[Session.Language]["Months"][1])
        Session.Current_month = 1
    load_categories_data()


def previous_month():
    Session.Current_month -= 1
    if Session.Current_month != 0:
        MainWindow.current_month.setText(LANGUAGES[Session.Language]["Months"][Session.Current_month])
    else:
        MainWindow.current_month.setText(LANGUAGES[Session.Language]["Months"][12])
        Session.Current_month = 12
    load_categories_data()


def next_year():
    Session.Current_year += 1
    MainWindow.current_year.setText(str(Session.Current_year))
    load_categories_data()


def previous_year():
    Session.Current_year -= 1
    MainWindow.current_year.setText(str(Session.Current_year))
    load_categories_data()