from GUI import *
from Languages import LANGUAGES
from Accont_mangment import Account


def get_min_and_max_categories(unsorted_categories:list,year:int,month:int,account:Account)->tuple:
    Categories_total_values = {}

    for category in unsorted_categories:
        Categories_total_values[category] = sum([transaction[5] for transaction in account.get_transactions_by_month(category,year,month)])

    highest_total_value = max([total_value for total_value in Categories_total_values.values()])

    def get_min_and_max_transactions(transactions:dict):
        #Highest transactions
        highest_transaction_value = max([transaction[5] for transaction in transactions])
        transactions_with_highest_value = [transaction[6] for transaction in transactions if transaction[5] == highest_transaction_value]

        transactions_names = [name for name in transactions_with_highest_value]
        transactions_with_highest_value = {}
        for transaction_name in set(transactions_names):
            transactions_with_highest_value[transaction_name] = transactions_names.count(transaction_name)
        transactions_with_highest_value["Highest value"] = highest_transaction_value
        
        #Lowest transactions
        lowest_transaction_value = min([transaction[5] for transaction in transactions])
        transactions_with_lowest_value = [transaction[6] for transaction in transactions if transaction[5] == lowest_transaction_value]

        transactions_names = [name for name in transactions_with_lowest_value]
        transactions_with_lowest_value = {}
        for transaction_name in set(transactions_names):
            transactions_with_lowest_value[transaction_name] = transactions_names.count(transaction_name)
        transactions_with_lowest_value["Lowest value"] = lowest_transaction_value

        return (transactions_with_highest_value,transactions_with_lowest_value)

    #Highest categories
    Categories_with_highest_total_value = {}
    for category in Categories_total_values:
        if Categories_total_values[category] == highest_total_value:
            transactions = account.get_transactions_by_month(category,year,month)
            transactions_statistic = get_min_and_max_transactions(transactions)
            Categories_with_highest_total_value[category] = [transactions_statistic[0],transactions_statistic[1]]
    Categories_with_highest_total_value["Highest total value"] = highest_total_value

    #Lowest categories
    for category,total_value in Categories_total_values.copy().items():
        if total_value == 0:
            del Categories_total_values[category]

    if len(Categories_total_values) != 0:
        lowest_total_value = min([total_value for total_value in Categories_total_values.values() if total_value])
        Categories_with_lowest_total_value = {}
        for category in Categories_total_values:
            if Categories_total_values[category] == lowest_total_value and Categories_total_values[category] != highest_total_value:#If we have only one category don't add it to lowest categories (it is already highest)
                transactions = account.get_transactions_by_month(category,year,month)
                transactions_statistic = get_min_and_max_transactions(transactions)
                Categories_with_lowest_total_value[category] = [transactions_statistic[0],transactions_statistic[1]]
        Categories_with_lowest_total_value["Lowest total value"] = lowest_total_value

    return (Categories_with_highest_total_value,Categories_with_lowest_total_value,Categories_total_values)


def add_statistic(statistic_list:QListWidget,statistic_data:dict,words:list,Language:str,Categories:dict):

    def add_highest_and_lowest_transactions(category:int,statistic:dict):
        #Highest transactions
        statistic_list.addItem("")
        statistic_list.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][words[4]])
        for transaction_name,transaction_value in statistic[category][0].items():
            if transaction_name != "Highest value":
                if transaction_name == "":
                    transaction_name = LANGUAGES[Language]["Account"]["Info"]["Statistics"][12]
                statistic_list.addItem(f"{transaction_name} - {statistic[category][0]['Highest value']}" if transaction_value == 1 else f"{transaction_value}x {transaction_name} - {statistic[category][0]['Highest value']}")
        
        #Lowest transactions
        if statistic[category][1]["Lowest value"] != statistic[category][0]["Highest value"]:
            statistic_list.addItem("")
            statistic_list.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][words[5]])
            for transaction_name,transaction_value in statistic[category][1].items():
                if transaction_name != "Lowest value":
                    if transaction_name == "":
                        transaction_name = LANGUAGES[Language]["Account"]["Info"]["Statistics"][12]
                    statistic_list.addItem(f"{transaction_name} - {statistic[category][1]['Lowest value']}" if transaction_value == 1 else f"{transaction_value}x {transaction_name} - {statistic[category][1]['Lowest value']}")
    
    #Highest category
    if len(statistic_data[0]) == 2:
        most_category = [*statistic_data[0].keys()][0]
        statistic_list.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][words[0]]+Categories[most_category]["Name"]+f"  ({statistic_data[0]['Highest total value']})")
        add_highest_and_lowest_transactions(most_category,statistic_data[0])
    elif len(statistic_data[0]) > 2:#Highest categories
        highest_categories = [category for category in statistic_data[0] if category != "Highest total value"]
        highest_categories_names = str((*[Categories[category]['Name'] for category in highest_categories],)).replace("'","")
        statistic_list.addItem(f"{LANGUAGES[Language]['Account']['Info']['Statistics'][words[1]]}  {highest_categories_names}  ({statistic_data[0]['Highest total value']})")

        for category in highest_categories:
            statistic_list.addItem("")
            statistic_list.addItem(f"{LANGUAGES[Language]['Account']['Info']['Statistics'][16]} {Categories[category]['Name']}")
            add_highest_and_lowest_transactions(category,statistic_data[0])

    #Lowest category
    if len(statistic_data[1]) == 2:
        least_category = [*statistic_data[1].keys()][0] 
        statistic_list.addItem("")
        statistic_list.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][words[2]]+Categories[least_category]["Name"]+f" ({statistic_data[1]['Lowest total value']})")
        add_highest_and_lowest_transactions(least_category,statistic_data[1])
    elif len(statistic_data[1]) > 2:#Lowest categories
        statistic_list.addItem("")
        statistic_list.addItem("")
        lowest_categories = [category for category in statistic_data[1] if category != "Lowest total value"]
        lowest_categories_names = str((*[Categories[category]['Name'] for category in lowest_categories],)).replace("'","")
        statistic_list.addItem(f"{LANGUAGES[Language]['Account']['Info']['Statistics'][words[3]]}  {lowest_categories_names}  ({statistic_data[1]['Lowest total value']})")

        for category in lowest_categories:
            statistic_list.addItem("")
            statistic_list.addItem(f"{LANGUAGES[Language]['Account']['Info']['Statistics'][16]} {Categories[category]['Name']}")
            add_highest_and_lowest_transactions(category,statistic_data[1])


def show_monthly_statistics(Categories:dict,Language:str,Current_year:int,Current_month:int,account:Account,months_days:list):
    Monthly_statistics.window.setWindowTitle(LANGUAGES[Language]["Months"][Current_month])
    Monthly_statistics.statistics.clear()
    if len(Categories) > 0:
        Incomes_categories = [category for category in Categories if Categories[category]["Type"] == "Incomes"]
        Expenses_categories = [category for category in Categories if Categories[category]["Type"] == "Expenses"]
        if not len(Incomes_categories) or not len(Expenses_categories):
            if len(account.get_transactions_by_month(Incomes_categories[0],Current_year,Current_month)) or len(account.get_transactions_by_month(Expenses_categories[0],Current_year,Current_month)):
                Incomes_statistic = get_min_and_max_categories(Incomes_categories,Current_year,Current_month,account)
                Expenses_statistic = get_min_and_max_categories(Expenses_categories,Current_year,Current_month,account)

                total_income = sum([Incomes_statistic[2][total_value] for total_value in Incomes_statistic[2]])
                total_expense = sum([Expenses_statistic[2][total_value] for total_value in Expenses_statistic[2]])
                days_amount = months_days[Current_month-1] + (Current_month == 2 and Current_year % 4 == 0)#Add one day to February (29) if year is leap

                Monthly_statistics.statistics.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][4]+str(total_income))
                Monthly_statistics.statistics.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][5]+f"{total_income/days_amount:.2f}")
                Monthly_statistics.statistics.addItem("")
                Monthly_statistics.statistics.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][6]+str(total_expense))
                Monthly_statistics.statistics.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][7]+f"{total_expense/days_amount:.2f}")
                Monthly_statistics.statistics.addItem("")
                Monthly_statistics.statistics.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][8]+f"{total_income - total_expense}")

                Monthly_statistics.statistics.addItem("")
                Monthly_statistics.statistics.addItem("")
                Monthly_statistics.statistics.addItem(LANGUAGES[Language]["Account"]["Info"][4])
                add_statistic(Monthly_statistics.statistics,Incomes_statistic,[9,10,13,14,11,15],Language,Categories)
                Monthly_statistics.statistics.addItem("")
                Monthly_statistics.statistics.addItem("")
                Monthly_statistics.statistics.addItem(LANGUAGES[Language]["Account"]["Info"][5])
                add_statistic(Monthly_statistics.statistics,Expenses_statistic,[17,18,20,21,19,22],Language,Categories)
                    
                Monthly_statistics.window.exec()
            else:
                Errors.no_category_error.exec()
        else:
            Errors.no_transactions_error.exec()
    else:
        Errors.no_category_error.exec()


def show_quarterly_statistics(Categories:dict,Language:str,Current_year:int,account:Account,months_days:list):

    #Clear quarters statistics
    for quarter in Quarterly_statistics.statistics:
        for statistic_list in Quarterly_statistics.statistics[quarter]:
            if statistic_list != "Label":
                Quarterly_statistics.statistics[quarter][statistic_list]["Statistic Data"].clear()

    if len(Categories):
        Incomes_categories = [category for category in Categories if Categories[category]["Type"] == "Incomes"]
        Expenses_categories = [category for category in Categories if Categories[category]["Type"] == "Expenses"]
        if len(Expenses_categories) > 1 and len(Incomes_categories) > 1:

            month_numbers = [(1,2,3),(4,5,6),(7,8,9),(10,11,12)]
            for quarter in Quarterly_statistics.statistics:
                Incomes_categories_total_values = {}
                Expenses_categories_total_values = {}
                for income_category,expenses_category in zip(Incomes_categories,Expenses_categories):

                    Incomes_categories_total_values[income_category] = []
                    Expenses_categories_total_values[expenses_category] = []

                    for month in range(3):
                        Incomes_categories_total_values[income_category].append(sum(transaction[5] for transaction in account.get_transactions_by_month(income_category,Current_year,month_numbers[quarter-1][month])))
                        Expenses_categories_total_values[expenses_category].append(sum(transaction[5] for transaction in account.get_transactions_by_month(expenses_category,Current_year,month_numbers[quarter-1][month])))

                    Incomes_categories_total_values[income_category] = sum(Incomes_categories_total_values[income_category])
                    Expenses_categories_total_values[expenses_category] = sum(Expenses_categories_total_values[expenses_category])
                
                #Entire quarter statistics
                total_income = sum(total_value for total_value in Incomes_categories_total_values.values())
                total_expense = sum(total_value for total_value in Expenses_categories_total_values.values())
                days_amount = sum(months_days[:3]) if quarter == 0 else sum(months_days[3:6]) if quarter ==  1 else sum(months_days[6:9]) if months_days == 2 else sum(months_days[9:12])

                Statistic_data = Quarterly_statistics.statistics[quarter][0]["Statistic Data"]
                Statistic_words = LANGUAGES[Language]["Account"]["Info"]["Statistics"]

                Statistic_data.addItem(Statistic_words[4]+str(total_income))
                Statistic_data.addItem(Statistic_words[5]+f"{total_income/days_amount:.2f}")
                Statistic_data.addItem("")
                Statistic_data.addItem(Statistic_words[6]+str(total_expense))
                Statistic_data.addItem(Statistic_words[7]+f"{total_expense/days_amount:.2f}")
                Statistic_data.addItem("")
                Statistic_data.addItem(Statistic_words[8]+str(total_income-total_expense))

                def add_total_statistics(statistic:dict,words:list):
                    max_total_value  = max(total_value for total_value in statistic.values())
                    min_total_value = min(total_value for total_value in statistic.values())

                    max_category = [category for category,total_value in statistic.items() if total_value == max_total_value ][0]
                    min_category = [category for category,total_value in statistic.items() if total_value == min_total_value ][0]

                    Statistic_data.addItem(Statistic_words[words[0]]+Categories[max_category]["Name"]+f" ({max_total_value})")
                    Statistic_data.addItem("")
                    if min_category != max_category:
                        Statistic_data.addItem(Statistic_words[words[1]]+Categories[min_category]["Name"]+f" ({min_total_value})")
                    Statistic_data.addItem("")

                    sorted_income_categories = dict(sorted(statistic.items(),key=lambda x:x[1],reverse=True))
                    for category,total_value in sorted_income_categories.items():
                        Statistic_data.addItem(f"{Categories[category]['Name']} - {total_value}")

                Statistic_data.addItem("")
                Statistic_data.addItem("")
                Statistic_data.addItem(LANGUAGES[Language]["Account"]["Info"][4])
                add_total_statistics(Incomes_categories_total_values,[9,13])

                Statistic_data.addItem("")
                Statistic_data.addItem("")
                Statistic_data.addItem(LANGUAGES[Language]["Account"]["Info"][5])
                add_total_statistics(Expenses_categories_total_values,[17,20])

                #Months statistics
                for month in range(3):
                    current_month = month_numbers[quarter-1][month]
                    if len(account.get_transactions_by_month(Incomes_categories[0],Current_year,current_month)) or len(account.get_transactions_by_month(Expenses_categories[0],Current_year,current_month)):
                        Incomes_statistic = get_min_and_max_categories(Incomes_categories,Current_year,current_month,account)
                        Expenses_statistic = get_min_and_max_categories(Expenses_categories,Current_year,current_month,account)

                        total_income = sum([Incomes_statistic[2][total_value] for total_value in Incomes_statistic[2]])
                        total_expense = sum([Expenses_statistic[2][total_value] for total_value in Expenses_statistic[2]])
                        days_amount = months_days[current_month-1] + (current_month == 2 and Current_year % 4 == 0)#Add one day to February (29) if year is leap
                        month_statistics = Quarterly_statistics.statistics[quarter][month+1]["Statistic Data"]

                        month_statistics.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][4]+str(total_income))
                        month_statistics.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][5]+f"{total_income/days_amount:.2f}")
                        month_statistics.addItem("")
                        month_statistics.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][6]+str(total_expense))
                        month_statistics.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][7]+f"{total_expense/days_amount:.2f}")
                        month_statistics.addItem("")
                        month_statistics.addItem(LANGUAGES[Language]["Account"]["Info"]["Statistics"][8]+f"{total_income - total_expense}")

                        month_statistics.addItem("")
                        month_statistics.addItem("")
                        month_statistics.addItem(LANGUAGES[Language]["Account"]["Info"][4])
                        add_statistic(month_statistics,Incomes_statistic,[9,10,13,14,11,15],Language,Categories)
                        month_statistics.addItem("")
                        month_statistics.addItem("")
                        month_statistics.addItem(LANGUAGES[Language]["Account"]["Info"][5])
                        add_statistic(month_statistics,Expenses_statistic,[17,18,20,21,19,22],Language,Categories)
                    else:
                        Quarterly_statistics.statistics[quarter][month+1]["Statistic Data"].addItem(Errors.no_transactions_error.text())
            Quarterly_statistics.window.exec()
        else:
            Errors.no_category_error.exec()


            
            