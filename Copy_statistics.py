from GUI import InformationMessage, MainWindow, CategorySettingsWindow, QApplication
from Project_configuration import CATEGORY_TYPE
from Account_management import Account
from Languages import LANGUAGES
# import pandas

def show_information_message():
    CategorySettingsWindow.copy_transactions.setEnabled(False)
    screen_center = MainWindow.window.frameGeometry().center()
    InformationMessage.window.move(screen_center)

    message_worker = InformationMessage.Worker()
    InformationMessage.threadpool.start(message_worker)
    


def copy_month_transactions(account: Account, Current_month:int, Current_year:int, Language:str, app:QApplication):
    print(CategorySettingsWindow.copy_transactions.isEnabled())
    if CategorySettingsWindow.copy_transactions.isEnabled():
        category_name = CategorySettingsWindow.window.windowTitle()
        category_id = account.get_category_id(category_name, CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()])
        
        transactions = account.get_transactions_by_month(category_id, Current_year, Current_month)
        if len(transactions):
            result = f"{LANGUAGES[Language]['Months'][Current_month]}\n{Current_year}\n"
            for transaction in transactions:
                result += f"{transaction[6]}    {transaction[4]}    {transaction[5]}\n"

            app.clipboard().setText(result)
            show_information_message()




    
