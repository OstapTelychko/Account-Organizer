from decimal import Decimal

from AppObjects.Session import Session
from GUI import *
from languages import LANGUAGES
from project_configuration import MONTHS_DAYS



def get_min_and_max_categories(unsorted_categories:list, current_month:str) -> tuple:
    Categories_total_values = {}

    for category in unsorted_categories:
        Categories_total_values[category] = float(sum([Decimal(transaction[5]) for transaction in Session.account.get_transactions_by_month(category, Session.current_year, current_month)]))

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

        return (transactions_with_highest_value, transactions_with_lowest_value)


    #Highest categories
    Categories_with_highest_total_value = {}
    for category in Categories_total_values:
        if Categories_total_values[category] == highest_total_value:
            transactions = Session.account.get_transactions_by_month(category, Session.current_year, current_month)
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
                transactions = Session.account.get_transactions_by_month(category, Session.current_year, current_month)
                transactions_statistic = get_min_and_max_transactions(transactions)
                Categories_with_lowest_total_value[category] = [transactions_statistic[0], transactions_statistic[1]]
        Categories_with_lowest_total_value["Lowest total value"] = lowest_total_value

    return (Categories_with_highest_total_value, Categories_with_lowest_total_value, Categories_total_values)


def add_statistic(statistic_list:QListWidget, statistic_data:dict, words:list):

    def add_highest_and_lowest_transactions(category:int, statistic:dict):
        #Highest transactions
        statistic_list.addItem("")
        statistic_list.addItem(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][words[4]])
        for transaction_name, transaction_value in statistic[category][0].items():
            if transaction_name != "Highest value":
                if transaction_name == "":
                    transaction_name = LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][12]
                statistic_list.addItem(f"{transaction_name} - {statistic[category][0]['Highest value']}" if transaction_value == 1 else f"{transaction_value}x {transaction_name} - {statistic[category][0]['Highest value']}")
        
        #Lowest transactions
        if statistic[category][1]["Lowest value"] != statistic[category][0]["Highest value"]:
            statistic_list.addItem("")
            statistic_list.addItem(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][words[5]])
            for transaction_name,transaction_value in statistic[category][1].items():
                if transaction_name != "Lowest value":
                    if transaction_name == "":
                        transaction_name = LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][12]
                    statistic_list.addItem(f"{transaction_name} - {statistic[category][1]['Lowest value']}" if transaction_value == 1 else f"{transaction_value}x {transaction_name} - {statistic[category][1]['Lowest value']}")
    
    #Highest category
    if len(statistic_data[0]) == 2:
        most_category = [*statistic_data[0].keys()][0]
        statistic_list.addItem(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][words[0]] + Session.categories[most_category].name+f"  ({statistic_data[0]['Highest total value']})")
        add_highest_and_lowest_transactions(most_category,statistic_data[0])

    elif len(statistic_data[0]) > 2:#Highest categories
        highest_categories = [category for category in statistic_data[0] if category != "Highest total value"]
        highest_categories_names = str((*[Session.categories[category].name for category in highest_categories],)).replace("'","")
        statistic_list.addItem(f"{LANGUAGES[Session.language]['Account']['Info']['Statistics'][words[1]]}  {highest_categories_names}  ({statistic_data[0]['Highest total value']})")

        for category in highest_categories:
            statistic_list.addItem("")
            statistic_list.addItem(f"{LANGUAGES[Session.language]['Account']['Info']['Statistics'][16]} {Session.categories[category].name}")
            add_highest_and_lowest_transactions(category, statistic_data[0])

    #Lowest category
    if len(statistic_data[1]) == 2:
        least_category = [*statistic_data[1].keys()][0] 
        statistic_list.addItem("")
        statistic_list.addItem(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][words[2]]+Session.categories[least_category].name+f" ({statistic_data[1]['Lowest total value']})")
        add_highest_and_lowest_transactions(least_category, statistic_data[1])
    elif len(statistic_data[1]) > 2:#Lowest categories
        statistic_list.addItem("")
        statistic_list.addItem("")
        lowest_categories = [category for category in statistic_data[1] if category != "Lowest total value"]
        lowest_categories_names = str((*[Session.categories[category].name for category in lowest_categories],)).replace("'","")
        statistic_list.addItem(f"{LANGUAGES[Session.language]['Account']['Info']['Statistics'][words[3]]}  {lowest_categories_names}  ({statistic_data[1]['Lowest total value']})")

        for category in lowest_categories:
            statistic_list.addItem("")
            statistic_list.addItem(f"{LANGUAGES[Session.language]['Account']['Info']['Statistics'][16]} {Session.categories[category].name}")
            add_highest_and_lowest_transactions(category, statistic_data[1])


def show_monthly_statistics():
    MonthlyStatistics.window.setWindowTitle(LANGUAGES[Session.language]["Months"][Session.current_month])
    MonthlyStatistics.statistics.clear()

    if len(Session.categories) >= 2:
        Incomes_categories = [category for category in Session.categories if Session.categories[category].type == "Incomes"]
        Expenses_categories = [category for category in Session.categories if Session.categories[category].type == "Expenses"]
        Incomes_categories_have_transactions = any([bool(len(Session.account.get_transactions_by_month(category, Session.current_year, Session.current_month))) for category in Incomes_categories])
        Expenses_categories_have_transactions = any([bool(len(Session.account.get_transactions_by_month(category, Session.current_year, Session.current_month))) for category in Expenses_categories])

        if  len(Incomes_categories) >= 1 and  len(Expenses_categories) >= 1:
            if Incomes_categories_have_transactions and Expenses_categories_have_transactions:
                Incomes_statistic = get_min_and_max_categories(Incomes_categories, Session.current_month)
                Expenses_statistic = get_min_and_max_categories(Expenses_categories, Session.current_month)

                total_income = sum([Incomes_statistic[2][total_value] for total_value in Incomes_statistic[2]])
                total_expense = sum([Expenses_statistic[2][total_value] for total_value in Expenses_statistic[2]])
                days_amount = MONTHS_DAYS[Session.current_month-1] + (Session.current_month == 2 and Session.current_year % 4 == 0)#Add one day to February (29) if year is leap

                MonthlyStatistics.statistics.addItem(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][4]+str(total_income))
                MonthlyStatistics.statistics.addItem(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][5]+str(float(Decimal(total_income)/days_amount)))
                MonthlyStatistics.statistics.addItem("")
                MonthlyStatistics.statistics.addItem(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][6]+str(total_expense))
                MonthlyStatistics.statistics.addItem(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][7]+str(float(Decimal(total_expense)/days_amount)))
                MonthlyStatistics.statistics.addItem("")
                MonthlyStatistics.statistics.addItem(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][8]+str(float(Decimal(total_income) - Decimal(total_expense))))

                MonthlyStatistics.statistics.addItem("")
                MonthlyStatistics.statistics.addItem("")
                MonthlyStatistics.statistics.addItem(LANGUAGES[Session.language]["Account"]["Info"][4])
                add_statistic(MonthlyStatistics.statistics, Incomes_statistic, [9,10,13,14,11,15])
                MonthlyStatistics.statistics.addItem("")
                MonthlyStatistics.statistics.addItem("")
                MonthlyStatistics.statistics.addItem(LANGUAGES[Session.language]["Account"]["Info"][5])
                add_statistic(MonthlyStatistics.statistics, Expenses_statistic, [17,18,20,21,19,22])
                    
                StatisticsWindow.window.done(1)
                MonthlyStatistics.window.exec()
            else:
                Errors.no_transactions.exec()
        else:
            Errors.no_category.exec()
    else:
        Errors.no_category.exec()


def add_month_statistics(Incomes_categories:dict, Expenses_categories:dict, Statistic_words:dict, month_statistics:QListWidget, current_month:str):
    Incomes_statistic = get_min_and_max_categories(Incomes_categories, current_month)
    Expenses_statistic = get_min_and_max_categories(Expenses_categories, current_month)

    total_income = float(sum([Decimal(Incomes_statistic[2][total_value]) for total_value in Incomes_statistic[2]]))
    total_expense = float(sum([Decimal(Expenses_statistic[2][total_value]) for total_value in Expenses_statistic[2]]))
    days_amount = MONTHS_DAYS[Session.current_month-1] + (Session.current_month == 2 and Session.current_year % 4 == 0)#Add one day to February (29) if year is leap

    month_statistics.addItem(Statistic_words[4]+str(total_income))
    month_statistics.addItem(Statistic_words[5]+str(float(Decimal(total_income)/days_amount)))
    month_statistics.addItem("")
    month_statistics.addItem(Statistic_words[6]+str(total_expense))
    month_statistics.addItem(Statistic_words[7]+str(float(Decimal(total_expense)/days_amount)))
    month_statistics.addItem("")
    month_statistics.addItem(Statistic_words[8]+str(float(Decimal(total_income) - Decimal(total_expense))))

    month_statistics.addItem("")
    month_statistics.addItem("")
    month_statistics.addItem(LANGUAGES[Session.language]["Account"]["Info"][4])
    add_statistic(month_statistics, Incomes_statistic, [9,10,13,14,11,15])
    month_statistics.addItem("")
    month_statistics.addItem("")
    month_statistics.addItem(LANGUAGES[Session.language]["Account"]["Info"][5])
    add_statistic(month_statistics, Expenses_statistic, [17,18,20,21,19,22])


def show_quarterly_statistics():

    #Clear quarters statistics
    for quarter in QuarterlyStatistics.statistics:
        for statistic_list in QuarterlyStatistics.statistics[quarter]:
            if statistic_list != "Label":
                QuarterlyStatistics.statistics[quarter][statistic_list]["Statistic Data"].clear()

    if len(Session.categories) >= 2:
        Incomes_categories = [category for category in Session.categories if Session.categories[category].type == "Incomes"]
        Expenses_categories = [category for category in Session.categories if Session.categories[category].type == "Expenses"]
        if len(Expenses_categories) >= 1 and len(Incomes_categories) >= 1:

            month_numbers = [(1,2,3),(4,5,6),(7,8,9),(10,11,12)]
            for quarter in QuarterlyStatistics.statistics:
                Incomes_categories_total_values = {}
                Expenses_categories_total_values = {}

                for income_category in Incomes_categories:
                    Incomes_categories_total_values[income_category] = []

                    for month in range(3):
                        Incomes_categories_total_values[income_category].append(float(sum(Decimal(transaction[5]) for transaction in Session.account.get_transactions_by_month(income_category, Session.current_year, month_numbers[quarter-1][month]))))
                    Incomes_categories_total_values[income_category] = sum(Incomes_categories_total_values[income_category])
                
                for expenses_category in Expenses_categories:
                    Expenses_categories_total_values[expenses_category] = []

                    for month in range(3):
                        Expenses_categories_total_values[expenses_category].append(float(sum(Decimal(transaction[5]) for transaction in Session.account.get_transactions_by_month(expenses_category, Session.current_year, month_numbers[quarter-1][month]))))
                    Expenses_categories_total_values[expenses_category] = sum(Expenses_categories_total_values[expenses_category])

                #Entire quarter statistics
                total_income = float(sum(Decimal(total_value) for total_value in Incomes_categories_total_values.values()))
                total_expense = float(sum(Decimal(total_value) for total_value in Expenses_categories_total_values.values()))
                days_amount = sum(MONTHS_DAYS[:3]) if quarter == 0 else sum(MONTHS_DAYS[3:6]) if quarter ==  1 else sum(MONTHS_DAYS[6:9]) if MONTHS_DAYS == 2 else sum(MONTHS_DAYS[9:12])

                Total_statistic_list = QuarterlyStatistics.statistics[quarter][0]["Statistic Data"]
                Statistic_words = LANGUAGES[Session.language]["Account"]["Info"]["Statistics"]

                Total_statistic_list.addItem(Statistic_words[4]+str(total_income))
                Total_statistic_list.addItem(Statistic_words[5]+str(float(Decimal(total_income)/days_amount)))
                Total_statistic_list.addItem("")
                Total_statistic_list.addItem(Statistic_words[6]+str(total_expense))
                Total_statistic_list.addItem(Statistic_words[7]+str(float(Decimal(total_expense)/days_amount)))
                Total_statistic_list.addItem("")
                Total_statistic_list.addItem(Statistic_words[8]+str(float(Decimal(total_income) - Decimal(total_expense))))

                def add_total_statistics(statistic:dict,words:list):
                    max_total_value  = max(total_value for total_value in statistic.values())
                    min_total_value = min(total_value for total_value in statistic.values())

                    max_category = [category for category,total_value in statistic.items() if total_value == max_total_value ][0]
                    min_category = [category for category,total_value in statistic.items() if total_value == min_total_value ][0]

                    Total_statistic_list.addItem(Statistic_words[words[0]] + Session.categories[max_category].name + f" ({max_total_value})")
                    Total_statistic_list.addItem("")
                    if min_category != max_category:
                        Total_statistic_list.addItem(Statistic_words[words[1]] + Session.categories[min_category].name + f" ({min_total_value})")
                    Total_statistic_list.addItem("")

                    sorted_income_categories = dict(sorted(statistic.items(), key=lambda x:x[1],reverse=True))
                    for category,total_value in sorted_income_categories.items():
                        Total_statistic_list.addItem(f"{Session.categories[category].name} - {total_value}")

                Total_statistic_list.addItem("")
                Total_statistic_list.addItem("")
                Total_statistic_list.addItem(LANGUAGES[Session.language]["Account"]["Info"][4])
                add_total_statistics(Incomes_categories_total_values, [9,13])

                Total_statistic_list.addItem("")
                Total_statistic_list.addItem("")
                Total_statistic_list.addItem(LANGUAGES[Session.language]["Account"]["Info"][5])
                add_total_statistics(Expenses_categories_total_values, [17,20])

                #Months statistics
                for month in range(3):
                    current_month = month_numbers[quarter-1][month]
                    Incomes_categories_have_transactions = any([bool(len(Session.account.get_transactions_by_month(category, Session.current_year, current_month))) for category in Incomes_categories])
                    Expenses_categories_have_transactions = any([bool(len(Session.account.get_transactions_by_month(category, Session.current_year, current_month))) for category in Expenses_categories])

                    if Incomes_categories_have_transactions and Expenses_categories_have_transactions:
                        add_month_statistics(Incomes_categories, Expenses_categories, Statistic_words, QuarterlyStatistics.statistics[quarter][month+1]["Statistic Data"], current_month)
                    else:
                        QuarterlyStatistics.statistics[quarter][month+1]["Statistic Data"].addItem(Errors.no_transactions.text())

            StatisticsWindow.window.done(1)
            QuarterlyStatistics.window.exec()
        else:
            Errors.no_category.exec()
    else:
        Errors.no_category.exec()


def show_yearly_statistics():
    #Clear yearly statistics
    for statistic_list in YearlyStatistics.statistics:
        YearlyStatistics.statistics[statistic_list]["Statistic Data"].clear()
    
    if len(Session.categories) >= 2:
        Incomes_categories = [category for category in Session.categories if Session.categories[category].type == "Incomes"]
        Expenses_categories = [category for category in Session.categories if Session.categories[category].type == "Expenses"]
        if len(Expenses_categories) >= 1 and len(Incomes_categories) >= 1:
            Incomes_categories_total_values = {}
            Expenses_categories_total_values = {}

            for income_category in Incomes_categories:
                Incomes_categories_total_values[income_category] = []

                for month in range(1,13):
                    Incomes_categories_total_values[income_category].append(float(sum(Decimal(transaction[5]) for transaction in Session.account.get_transactions_by_month(income_category, Session.current_year,month))))
                Incomes_categories_total_values[income_category] = sum(Incomes_categories_total_values[income_category])
            
            for expenses_category in Expenses_categories:
                Expenses_categories_total_values[expenses_category] = []

                for month in range(1,13):
                    Expenses_categories_total_values[expenses_category].append(float(sum(Decimal(transaction[5]) for transaction in Session.account.get_transactions_by_month(expenses_category, Session.current_year,month))))
                Expenses_categories_total_values[expenses_category] = sum(Expenses_categories_total_values[expenses_category])

            #Entire year statistics
            total_income = float(sum(Decimal(total_value) for total_value in Incomes_categories_total_values.values()))
            total_expense = float(sum(Decimal(total_value) for total_value in Expenses_categories_total_values.values()))
            days_amount = 365 if Session.current_year % 4 != 0 else 366# 365 days if year is not leap

            Total_statistic_list = YearlyStatistics.statistics[0]["Statistic Data"]
            Statistic_words = LANGUAGES[Session.language]["Account"]["Info"]["Statistics"]

            Total_statistic_list.addItem(Statistic_words[4]+str(total_income))
            Total_statistic_list.addItem(Statistic_words[25]+str(float(Decimal(total_income)/12)))
            Total_statistic_list.addItem(Statistic_words[24]+str(float(Decimal(total_income)/days_amount)))
            Total_statistic_list.addItem("")
            Total_statistic_list.addItem(Statistic_words[6]+str(total_expense))
            Total_statistic_list.addItem(Statistic_words[27]+str(float(Decimal(total_expense)/12)))
            Total_statistic_list.addItem(Statistic_words[26]+str(float(Decimal(total_expense)/Decimal(days_amount))))
            Total_statistic_list.addItem("")
            Total_statistic_list.addItem(Statistic_words[8]+f"{float(Decimal(total_income)-Decimal(total_expense))}")

            def add_total_statistics(statistic:dict,words:list):
                max_total_value  = max(total_value for total_value in statistic.values())
                min_total_value = min(total_value for total_value in statistic.values())

                max_category = [category for category,total_value in statistic.items() if total_value == max_total_value ][0]
                min_category = [category for category,total_value in statistic.items() if total_value == min_total_value ][0]

                Total_statistic_list.addItem(Statistic_words[words[0]] + Session.categories[max_category].name+f" ({max_total_value})")
                Total_statistic_list.addItem("")
                if min_category != max_category:
                    Total_statistic_list.addItem(Statistic_words[words[1]] + Session.categories[min_category].name+f" ({min_total_value})")
                Total_statistic_list.addItem("")

                sorted_categories = dict(sorted(statistic.items(), key=lambda category:category[1], reverse=True))
                for category, total_value in sorted_categories.items():
                    Total_statistic_list.addItem(f"{Session.categories[category].name} - {total_value}")

            Total_statistic_list.addItem("")
            Total_statistic_list.addItem("")
            Total_statistic_list.addItem(LANGUAGES[Session.language]["Account"]["Info"][4])
            add_total_statistics(Incomes_categories_total_values, [9,13])

            Total_statistic_list.addItem("")
            Total_statistic_list.addItem("")
            Total_statistic_list.addItem(LANGUAGES[Session.language]["Account"]["Info"][5])
            add_total_statistics(Expenses_categories_total_values, [17,20])

            for month in range(1,13):
                Incomes_categories_have_transactions = any([bool(len(Session.account.get_transactions_by_month(category, Session.current_year, month))) for category in Incomes_categories])
                Expenses_categories_have_transactions = any([bool(len(Session.account.get_transactions_by_month(category, Session.current_year, month))) for category in Expenses_categories])

                if Incomes_categories_have_transactions and Expenses_categories_have_transactions:
                    add_month_statistics(Incomes_categories, Expenses_categories, Statistic_words, YearlyStatistics.statistics[month]["Statistic Data"], month)
                else:
                    YearlyStatistics.statistics[month]["Statistic Data"].addItem(Errors.no_transactions.text())

            StatisticsWindow.window.done(1)
            YearlyStatistics.window.exec()
        else:
            Errors.no_category.exec()
    else:
        Errors.no_category.exec()

            