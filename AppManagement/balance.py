from Session import Session
from GUI import MainWindow, SettingsWindow
from languages import LANGUAGES


def calculate_current_balance():
    Session.current_total_income = 0
    Session.current_total_expenses = 0

    for category in Session.account.get_all_categories():

        if category[1] == "Incomes":
            for transaction in Session.account.get_all_transactions(category[0]):
                Session.current_total_income += transaction[5]

        elif category[1] == "Expenses":
            for transaction in Session.account.get_all_transactions(category[0]):
                Session.current_total_expenses += transaction[5]
    
    # If user created account recently with balance not 0 and he don't have transactions yet
    if Session.current_total_income == 0 and Session.current_total_expenses == 0 and Session.account.get_account_balance()[0] != 0:
        Session.current_balance = Session.account.get_account_balance()[0]
    else:
        Session.current_balance = Session.current_total_income - Session.current_total_expenses

    Session.account.update_account_balance(Session.current_balance, Session.current_total_income, Session.current_total_expenses)
    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Account"]["Info"][3]+str(round(Session.current_balance, 2)))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Account"]["Info"][7]+str(round(Session.current_total_income, 2)))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Account"]["Info"][8]+str(round(Session.current_total_expenses, 2)))


def load_account_balance():
    Session.current_balance, Session.current_total_income, Session.current_total_expenses = Session.account.get_account_balance()

    if Session.current_total_income == 0 and Session.current_total_expenses == 0:
        calculate_current_balance()
    
    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Account"]["Info"][3]+str(round(Session.current_balance, 2)))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Account"]["Info"][7]+str(round(Session.current_total_income, 2)))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Account"]["Info"][8]+str(round(Session.current_total_expenses, 2)))


def update_account_balance():
    Session.account.update_account_balance(Session.current_balance, Session.current_total_income, Session.current_total_expenses)

    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Account"]["Info"][3]+str(round(Session.current_balance,2)))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Account"]["Info"][7]+str(round(Session.current_total_income,2)))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Account"]["Info"][8]+str(round(Session.current_total_expenses,2)))