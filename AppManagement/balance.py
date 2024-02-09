from AppObjects.session import Session
from GUI.windows.main import MainWindow, SettingsWindow
from languages import LANGUAGES




def calculate_current_balance():
    Session.current_total_income = 0
    Session.current_total_expenses = 0

    for category in Session.account.get_all_categories():

        if category[1] == "Incomes":
            for transaction in Session.account.get_all_transactions(category[0]):
                Session.current_total_income += transaction.value

        elif category[1] == "Expenses":
            for transaction in Session.account.get_all_transactions(category[0]):
                Session.current_total_expenses += transaction.value
    
    Session.current_total_income = round(Session.current_total_income, 2)
    Session.current_total_expenses = round(Session.current_total_expenses, 2)

    # If user created account recently with balance not 0 and he don't have transactions yet
    if Session.current_total_income == 0 and Session.current_total_expenses == 0 and Session.account.get_account_balance()[0] != 0:
        Session.current_balance = Session.account.get_account_balance()[0]
    else:
        Session.current_balance = round(Session.current_total_income - Session.current_total_expenses, 2)

    Session.account.update_account_balance(Session.current_balance, Session.current_total_income, Session.current_total_expenses)
    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Account"]["Info"][3]+str(Session.current_balance))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Account"]["Info"][7]+str(Session.current_total_income))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Account"]["Info"][8]+str(Session.current_total_expenses))


def load_account_balance():
    Session.current_balance, Session.current_total_income, Session.current_total_expenses = Session.account.get_account_balance()

    if Session.current_total_income == 0 and Session.current_total_expenses == 0:
        calculate_current_balance()
    
    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Account"]["Info"][3]+str(Session.current_balance))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Account"]["Info"][7]+str(Session.current_total_income))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Account"]["Info"][8]+str(Session.current_total_expenses))


def update_account_balance():
    Session.account.update_account_balance(Session.current_balance, Session.current_total_income, Session.current_total_expenses)

    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Account"]["Info"][3]+str(Session.current_balance))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Account"]["Info"][7]+str(Session.current_total_income))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Account"]["Info"][8]+str(Session.current_total_expenses))