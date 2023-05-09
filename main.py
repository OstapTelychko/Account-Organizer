from GUI import *
from Languages import LANGUAGES
from Accont_mangment import Account
from datetime import datetime,date,timedelta
import toml
from calendar import monthrange

# print(calendar.monthrange(2023,4))

# today = date(2023,4,1)
# start = today - timedelta(days=today.weekday())
# end = start + timedelta(days=6)
# print("Today: " + str(today))
# print("Start: " + str(start.day))
# print("End: " + str(end.day))
# number = 0.4353535353
# print(f"{number:.0f}")
Current_balance = 0
Current_month = datetime.now().month
Current_year = datetime.now().year

Accounts_list = []
Categories = {}
CATEGORY_TYPE = {0:"Incomes",1:"Expenses"}

def update_config():
    with open("./configuration.toml","w",encoding="utf-8") as file:
        toml.dump(Configuration,file)


def swith_theme():
    global Configuration
    if Configuration["Theme"] == "Dark":
        app.setStyleSheet(light_theme)
        Settings_window.switch_themes_button.setIcon(light_theme_icon)

        if len(Categories) != 0:
            for category in Categories:
                Categories[category]["Category data"].setStyleSheet("QTableWidget{background-color:rgb(205,205,205)}")

        Configuration.update({"Theme" : "Light"})
    elif Configuration["Theme"] == "Light":
        app.setStyleSheet(dark_theme)
        Settings_window.switch_themes_button.setIcon(dark_theme_icon)

        if len(Categories) != 0:
            for category in Categories:
                Categories[category]["Category data"].setStyleSheet("QTableWidget{background-color:rgb(45,45,45)}")

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
    Main_window.Incomes_and_expenses.setTabText(0,LANGUAGES[Language]["Account"]["Info"][4])
    Main_window.Incomes_and_expenses.setTabText(1,LANGUAGES[Language]["Account"]["Info"][5])
    Main_window.add_incomes_category.setText(LANGUAGES[Language]["Account"]["Category management"][0])
    Main_window.add_expenses_category.setText(LANGUAGES[Language]["Account"]["Category management"][0])

    Settings_window.window.setWindowTitle(LANGUAGES[Language]["Windows"][0])
    Settings_window.delete_account.setText(LANGUAGES[Language]["Account"]["Account management"][0])
    Settings_window.add_account.setText(LANGUAGES[Language]["Account"]["Account management"][1])
    Settings_window.rename_account.setText(LANGUAGES[Language]["Account"]["Account management"][2])

    Add_accoount_window.window.setWindowTitle(LANGUAGES[Language]["Windows"][1])
    Add_accoount_window.name.setPlaceholderText(LANGUAGES[Language]["Account"][0])
    Add_accoount_window.surname.setPlaceholderText(LANGUAGES[Language]["Account"][1])

    Add_category_window.category_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][0])
    Add_category_window.button.setText(LANGUAGES[Language]["General management"][1])
    Add_category_window.window.setWindowTitle(LANGUAGES[Language]["Account"]["Category management"][0])

    Category_settings_window.delete_category.setText(LANGUAGES[Language]["Account"]["Category management"][1])
    Category_settings_window.rename_category.setText(LANGUAGES[Language]["Account"]["Category management"][2])
    Category_settings_window.show_statistics.setText(LANGUAGES[Language]["Account"]["Category management"][3])

    Rename_category_window.new_category_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Category management"][4])
    Rename_category_window.button.setText(LANGUAGES[Language]["General management"][2])

    Transaction_management_window.button.setText(LANGUAGES[Language]["General management"][5])
    Transaction_management_window.transaction_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][0])
    Transaction_management_window.transaction_day.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][1])
    Transaction_management_window.transaction_value.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][2])

    for index,error in enumerate(errors_list):
        error.setText(LANGUAGES[Language]["Errors"][index])
        error.button(QMessageBox.StandardButton.Ok).setText(LANGUAGES[Language]["General management"][3])
        if error.button(QMessageBox.StandardButton.Cancel) != None:
            error.button(QMessageBox.StandardButton.Cancel).setText(LANGUAGES[Language]["General management"][4])
    
    if len(Categories) > 0:
        for category in Categories:
            Categories[category]["Add transaction"].setText(LANGUAGES[Language]["Account"]["Transactions management"][0])
            Categories[category]["Delete transaction"].setText(LANGUAGES[Language]["Account"]["Transactions management"][1])
            Categories[category]["Edit transaction"].setText(LANGUAGES[Language]["Account"]["Transactions management"][2])
            Categories[category]["Category data"].setHorizontalHeaderLabels((LANGUAGES[Language]["Account"]["Info"][0],LANGUAGES[Language]["Account"]["Info"][1],LANGUAGES[Language]["Account"]["Info"][2]))
            total_value = Categories[category]["Total value"].text().split(" ")[1]
            Categories[category]["Total value"].setText(LANGUAGES[Language]["Account"]["Info"][6]+total_value)
    
    Main_window.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(Current_balance))
    Incomes = Settings_window.total_income.text().split(" ")[2]
    Settings_window.total_income.setText(LANGUAGES[Language]["Account"]["Info"][7]+str(Incomes))
    Expenses = Settings_window.total_expense.text().split(" ")[2]
    Settings_window.total_expense.setText(LANGUAGES[Language]["Account"]["Info"][8]+str(Expenses))
    Settings_window.account_created_date.setText(LANGUAGES[Language]["Account"]["Info"][9]+account.get_account_date())    


def calculate_current_balance():
    global Current_balance

    Incomes = 0
    Expenses = 0

    for category in account.get_all_categories():
        if category[1] == "Incomes":
            for transaction in account.get_all_transactions(category[0]):
                Incomes += transaction[5]
        elif category[1] == "Expenses":
            for transaction in account.get_all_transactions(category[0]):
                Expenses += transaction[5]
    
    Current_balance = Incomes - Expenses
    Main_window.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(Current_balance))
    Settings_window.total_income.setText(LANGUAGES[Language]["Account"]["Info"][7]+str(Incomes))
    Settings_window.total_expense.setText(LANGUAGES[Language]["Account"]["Info"][8]+str(Expenses))


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


def show_add_user_window():
    Add_accoount_window.message.setText(LANGUAGES[Language]["Account"]["Account management"]["Messages"][0])
    Add_accoount_window.button.setText(LANGUAGES[Language]["General management"][1])
    Add_accoount_window.window.exec()


def add_user():
    global Account_name,Configuration

    name = Add_accoount_window.name.text().strip()
    surname = Add_accoount_window.surname.text().strip()

    if name.isalpha() and surname.isalpha():
        full_name = name+" "+surname
        account  = Account("./Accounts.sqlite",full_name)
        if not account.account_exists():
            balance = Add_accoount_window.current_balance.text()
            if balance != "":
                if balance.isdigit():
                    account.create_account(int(balance))
                    Add_accoount_window.window.hide()
                    Account_name = full_name
                    Configuration.update({"Account_name":Account_name})
                    update_config()
                    Settings_window.accounts.addItem(full_name)
                    Accounts_list.append(Account_name)
                    Settings_window.accounts.setCurrentText(Account_name)
            else:
                if Errors.zero_current_balance_error.exec() == QMessageBox.StandardButton.Ok:
                    account.create_account(0)
                    Add_accoount_window.window.hide()
                    Account_name = full_name
                    Configuration.update({"Account_name":Account_name})
                    update_config()
                    Settings_window.accounts.addItem(full_name)
                    Accounts_list.append(Account_name)
                    Settings_window.accounts.setCurrentText(Account_name)
        else:
            Errors.account_alredy_exists_error.exec()
    else:
        Errors.incorrect_data_type_error.exec()


def create_category():
    global Categories

    category_type = "Incomes" if Main_window.Incomes_and_expenses.currentIndex() == 0 else "Expenses"
    category_name = Add_category_window.category_name.text().strip()

    if not account.category_exists(category_name,category_type):
        account.create_category(category_name,category_type)
        category_id = account.get_category_id(category_name,category_type) 
        Categories[category_id]=load_category(category_type,category_name,account,category_id,Current_year,Current_month,Language,Configuration["Theme"])
        activate_categories()
        Add_category_window.window.hide()
    else:
        Errors.category_exists_error.exec()


def load_categories():
    global Categories

    for category in account.get_all_categories():
        Categories[category[0]]=load_category(category[1],category[2],account,category[0],Current_year,Current_month,Language,Configuration["Theme"])


def show_category_settings(category_name:str):
    if account.category_exists(category_name,CATEGORY_TYPE[Main_window.Incomes_and_expenses.currentIndex()]):
        Category_settings_window.window.setWindowTitle(category_name)
        Category_settings_window.window.exec()


def remove_category():
    global Categories

    category_name = Category_settings_window.window.windowTitle()

    if Errors.delete_category_question.exec() == QMessageBox.StandardButton.Ok:
        category_id = account.get_category_id(category_name,CATEGORY_TYPE[Main_window.Incomes_and_expenses.currentIndex()])
        account.delete_category(category_id)
        Category_settings_window.window.setWindowTitle(" ")
        Category_settings_window.window.hide()

        Categories[category_id]["Category window"].deleteLater()
        Categories[category_id]["Settings"].deleteLater()
        Categories[category_id]["Add transaction"].deleteLater()
        Categories[category_id]["Edit transaction"].deleteLater()
        Categories[category_id]["Delete transaction"].deleteLater()
        del Categories[category_id]

        calculate_current_balance()


def rename_category():
    global Categories

    new_category_name = Rename_category_window.new_category_name.text().strip()
    current_name = Rename_category_window.window.windowTitle()
    category_type = CATEGORY_TYPE[Main_window.Incomes_and_expenses.currentIndex()]

    if not account.category_exists(new_category_name,category_type):
        for category in Categories:
            if Categories[category]["Name"] == current_name:
                Categories[category].update({"Name":new_category_name})
                Categories[category]["Settings"].clicked.connect(lambda category_name= new_category_name,useless_variable=False: show_category_settings(category_name=category_name,useless_variable=useless_variable))
                Categories[category]["Name label"].setText(new_category_name)
                account.rename_category(account.get_category_id(current_name,category_type),new_category_name)
                Rename_category_window.window.hide()
                Category_settings_window.window.hide()
    else:
        Errors.category_exists_error.exec()


def update_category_total_value(category_id:int):
    transactions = account.get_transactions_by_month(category_id,Current_year,Current_month)
    total_value = 0

    if len(transactions) != 0:
        for transaction in transactions:
            total_value += transaction[5]
    Categories[category_id]["Total value"].setText(LANGUAGES[Language]["Account"]["Info"][6]+str(total_value))
    

def show_edit_transaction_window(category_name:str,category_data:QTableWidget):
    selected_row = category_data.selectedItems()
    if len(selected_row) != 0 and  not len(selected_row) < 3:
        if len(selected_row) == 3 and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[2].row():
            Transaction_management_window.button.setText(LANGUAGES[Language]["General management"][5])
            Transaction_management_window.message.setText(LANGUAGES[Language]["Account"]["Transactions management"]["Messages"][0])
            Transaction_management_window.window.setWindowTitle(category_name)
            Transaction_management_window.transaction_name.setText(selected_row[0].text())
            Transaction_management_window.transaction_day.setText(selected_row[1].text)
            Transaction_management_window.transaction_value.setText(selected_row[2].text())
            Transaction_management_window.transaction_id = int(category_data.item(selected_row[0].row(),3).text())
            Transaction_management_window.window.exec()
        else:
            Errors.only_one_row_error.exec()
    else:
        Errors.unselected_row_error.exec()


def update_transaction(transaction_id:int,transaction_name:str,transaction_day:int,transaction_value:int|float,category_data:QTableWidget):
    account.update_transaction(transaction_id,transaction_name,transaction_day,transaction_value)
                
    for row in range(category_data.rowCount()):
        if int(category_data.item(row,3).text()) == transaction_id:
            category_data.item(row,0).setText(transaction_name)
            category_data.item(row,1).setData(Qt.ItemDataRole.EditRole,transaction_day)
            category_data.item(row,2).setData(Qt.ItemDataRole.EditRole,transaction_value)


def show_add_transaction_window(category_name:str):
    Transaction_management_window.button.setText(LANGUAGES[Language]["General management"][1])
    Transaction_management_window.message.setText(LANGUAGES[Language]["Account"]["Transactions management"]["Messages"][1])
    Transaction_management_window.transaction_name.setText("")
    Transaction_management_window.transaction_day.setText("")
    Transaction_management_window.transaction_value.setText("")

    Transaction_management_window.window.setWindowTitle(category_name)
    Transaction_management_window.window.exec()


def add_transaction(transaction_name:str,transaction_day:int,transaction_value:int|float,category_data:QTableWidget,category_id):
    account.add_transaction(category_id,Current_year,Current_month,transaction_day,transaction_value,transaction_name)

    row = category_data.rowCount()
    category_data.setRowCount(row+1)

    day = QTableWidgetItem()
    day.setData(Qt.ItemDataRole.DisplayRole,transaction_day)
    value = QTableWidgetItem()
    value.setData(Qt.ItemDataRole.DisplayRole,transaction_value)
    category_data.setItem(row,0,QTableWidgetItem(transaction_name))
    category_data.setItem(row,1,day)
    category_data.setItem(row,2,value)


def transaction_data_handler():
    transaction_name = Transaction_management_window.transaction_name.text().strip()
    transaction_day = Transaction_management_window.transaction_day.text()
    transaction_value = Transaction_management_window.transaction_value.text()
    transaction_id = Transaction_management_window.transaction_id
    category_id = account.get_category_id(Transaction_management_window.window.windowTitle(),CATEGORY_TYPE[Main_window.Incomes_and_expenses.currentIndex()])
    category_data = Categories[category_id]["Category data"]

    if  transaction_day != "" or transaction_value != "":
        if transaction_day.isalnum() and transaction_value.replace(".","").isdigit():
            transaction_day = int(transaction_day)
            max_month_day = monthrange(Current_year,Current_month)[1]
            if 0 < transaction_day <= max_month_day:
                if transaction_value.find("."):
                    transaction_value = float(transaction_value)
                else:
                    transaction_value = int(transaction_value)

                if Transaction_management_window.button.text() == LANGUAGES[Language]["General management"][5]: #Update 
                    update_transaction(transaction_id,transaction_name,transaction_day,transaction_value,category_data)
                else: #Add
                    add_transaction(transaction_name,transaction_day,transaction_value,category_data,category_id)

                update_category_total_value(category_id)
                calculate_current_balance()
                Transaction_management_window.window.hide()
            else:
                Errors.day_out_range_error.setText(LANGUAGES[Language]["Errors"][8]+f"1-{max_month_day}")
                Errors.day_out_range_error.exec()
        else:
            Errors.incorrect_data_type_error.exec()
    else:
        Errors.empty_fields_error.exec()


def remove_transaction(category_data:QTableWidget):
    selected_row = category_data.selectedItems()
    if len(selected_row) != 0 and  not len(selected_row) < 3:
        if len(selected_row) == 3 and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[2].row():
            print(category_data.item(0,3))
            transaction_id = category_data.item(selected_row[0].row(),3).data(Qt.ItemDataRole.EditRole)
            if Errors.delete_transaction_question.exec() == QMessageBox.StandardButton.Ok:
                account.delete_transaction(transaction_id)

                print(category_data.rowCount())
                for row in range(category_data.rowCount()):
                    if category_data.item(row,3).data(Qt.ItemDataRole.EditRole) == transaction_id:
                        category_data.removeRow(row)
                        break
                
                category_data.setRowCount(category_data.rowCount())
                header = category_data.horizontalHeader()
                header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                header.setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
                row = category_data.verticalHeader()
                row.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                print(category_data.rowCount())
        else:
            Errors.only_one_row_error.exec()
    else:
        Errors.unselected_row_error.exec()


def activate_categories():
    for category in Categories:
        Categories[category]["Settings"].clicked.connect(lambda category_name = Categories[category]["Name"],_=False: show_category_settings(category_name=category_name))
        Categories[category]["Add transaction"].clicked.connect(lambda category_name = Categories[category]["Name"],_=False: show_add_transaction_window(category_name))
        Categories[category]["Edit transaction"].clicked.connect(lambda category_name= Categories[category]["Name"],category_data = Categories[category]["Category data"]:show_edit_transaction_window(category_name=category_name,category_data=category_data))
        Categories[category]["Delete transaction"].clicked.connect(lambda category_data = Categories[category]["Category data"],_=False:remove_transaction(category_data))


if __name__ == "__main__":
    with open("./configuration.toml") as file:
        Configuration = toml.load("./configuration.toml")


    #Load selected language 
    Language = Configuration["Language"]
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
    #Settings
    Main_window.settings.clicked.connect(Settings_window.window.exec)
    Settings_window.switch_themes_button.clicked.connect(swith_theme)
    Settings_window.languages.currentIndexChanged.connect(change_language)
    Settings_window.add_account.clicked.connect(show_add_user_window)

    Add_accoount_window.button.clicked.connect(add_user)

    #Category settings
    Category_settings_window.delete_category.clicked.connect(remove_category)
    Category_settings_window.rename_category.clicked.connect(lambda: (Rename_category_window.window.setWindowTitle(Category_settings_window.window.windowTitle()),Rename_category_window.window.exec()))
    Rename_category_window.button.clicked.connect(rename_category)
    Transaction_management_window.button.clicked.connect(transaction_data_handler)
    
    #Date management
    Main_window.next_month_button.clicked.connect(next_month)
    Main_window.previous_month_button.clicked.connect(previous_month)
    Main_window.next_year_button.clicked.connect(next_year)
    Main_window.previous_year_button.clicked.connect(previous_year)

    #Add category
    Main_window.add_incomes_category.clicked.connect(Add_category_window.window.exec)
    Main_window.add_expenses_category.clicked.connect(Add_category_window.window.exec)
    Add_category_window.button.clicked.connect(create_category)

    #Load last used account name 
    Account_name = Configuration["Account_name"]

    #Create new account if it doesn't exist
    if Account_name == "":
        show_add_user_window()
    
    #Connect to db
    account = Account("./Accounts.sqlite",Account_name)
    account.get_account_id()

    #Load categories if they exists
    if len(account.get_all_categories()) > 0:
        load_categories()
    activate_categories()

    [Accounts_list.append(item[0]) for item in account.get_all_accounts()]
    Settings_window.accounts.addItems(Accounts_list)
    Settings_window.accounts.setCurrentText(Account_name)

    calculate_current_balance()
    change_language(Language)

    Main_window.window.show()
    app.exec()