from AppObjects.session import Session
from GUI.windows.main import MainWindow, SettingsWindow
from languages import LANGUAGES




def calculate_current_balance():
    Session.current_total_income = 0
    Session.current_total_expenses = 0

    for category in Session.db.get_all_categories():

        if category.category_type == "Incomes":
            for transaction in Session.db.get_all_transactions(category.id):
                Session.current_total_income += transaction.value

        elif category.category_type == "Expenses":
            for transaction in Session.db.get_all_transactions(category.id):
                Session.current_total_expenses += transaction.value
    
    Session.current_total_income = round(Session.current_total_income, 2)
    Session.current_total_expenses = round(Session.current_total_expenses, 2)

    Session.current_balance = Session.db.get_account().start_balance + round(Session.current_total_income - Session.current_total_expenses, 2)

    Session.db.update_account_balance(Session.current_balance, Session.current_total_income, Session.current_total_expenses)
    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Account"]["Info"][3]+str(Session.current_balance))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Account"]["Info"][7]+str(Session.current_total_income))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Account"]["Info"][8]+str(Session.current_total_expenses))


def load_account_balance():
    account = Session.db.get_account()
    Session.current_balance = account.current_balance
    Session.current_total_income = account.current_total_income
    Session.current_total_expenses = account.current_total_expenses

    if Session.current_total_income == 0 and Session.current_total_expenses == 0:
        calculate_current_balance()
    
    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Account"]["Info"][3]+str(Session.current_balance))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Account"]["Info"][7]+str(Session.current_total_income))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Account"]["Info"][8]+str(Session.current_total_expenses))


def update_account_balance():
    Session.db.update_account_balance(Session.current_balance, Session.current_total_income, Session.current_total_expenses)

    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Account"]["Info"][3]+str(Session.current_balance))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Account"]["Info"][7]+str(Session.current_total_income))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Account"]["Info"][8]+str(Session.current_total_expenses))