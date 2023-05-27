from GUI import *

LANGUAGES = {
    "English":{
        "Months":{
            1:"January",
            2:"February",
            3:"March",
            4:"April",
            5:"May",
            6:"June",
            7:"July",
            8:"August",
            9:"September",
            10:"October",
            11:"November",
            12:"December"
        },
        "General management":{
            0:"Delete",
            1:"Add",
            2:"Rename",
            3:"Ok",
            4:"Cancel",
            5:"Update"
        },
        "Account":{
            0:"Name",
            1:"Surname",
            2:"Current balance",
            "Account management":{
                0:"Delete account",
                1:"Create account",
                2:"Rename account",
                3:"New name",
                4:"New surname",
                "Messages":{
                    0:"Enter name and surname to create a new account. (You can't use the same full name)",
                    1:"Enter new name and surname to rename account. "
                }
            },
            "Info":{
                0:"Name",
                1:"Date",
                2:"Value",
                3:"Balance ",
                4:"Incomes",
                5:"Expenses",
                6:"Total: ",
                7:"Total income: ",
                8:"Total expense: ",
                9:"Created ",
                "Statistics":{
                    0:"Statistics",
                    1:"Monthly",
                    2:"Quarterly",
                    3:"Yearly",
                    4:"Total income ",
                    5:"Average income ",
                    6:"Total expenses ",
                    7:"Average expenses ",
                    8:"Income with expenses ",
                    9:"The most lucrative category ",
                    10:"The most lucrative categories ",
                    11:"The most lucrative transactions:",
                    12:"No name",
                    13:"The least lecrative category ",
                    14:"The least lecrative categories ",
                    15:"The least lucrative transactions:",
                    16:"Category ",
                    17:"The most expensive category ",
                    18:"The most expensive categories ",
                    19:"The most expensive transactions ",
                    20:"The cheapest category ",
                    21:"The cheapest categories ",
                    22:"The cheapest transactions ",

                }
            },
            "Transactions management":{
                0:"Add transaction",
                1:"Delete transaction",
                2:"Edit transaction",
                "Messages":{
                    0:"Enter the values you want to change",
                    1:"""
                    Enter the name (optional) day and value of transaction for example:

                                            Harry Potter    28      13850
                                            Salary              20      25000
                    """
                }
            },
            "Category management":{
                0:"Create category",
                1:"Delete category",
                2:"Rename category",
                4:"New name",
            }
        },
        "Errors":{
            0:"You have entered invalid type of data, check them again",
            1:"Account with this name alredy exists",
            2:"You haven't entered a current balance, i will count it as 0 (if that's not true value there may be discrepancy between current and actual balance)",
            3:"This category already exists",
            4:"Are you sure you want to delete the category? You will lose ALL transactions added to this category and your current balance will be recalculated",
            5:"Select transaction. (Click on transaction number to select)",
            6:"Please select only 1 row",
            7:"You can't leave the fields empty",
            8:"The day must be in range ",
            9:"Are you sure you want to remove transaction?",
            10:"Would you like to load account ?",
            11:"Are you sure you want to remove account ? This action is irreversible",
            12:"I can't calculate empty expression",
            13:"You have used forbidden word in expression",
            14:"You should have at least one category for income and one for expenses to see monthly statistics",
            15:"You should have at least one income transaction and one expense transaction to see monthly statistics"
        },
        "Mini calculator":{
            0:"Mini calculator",
            1:"You can't divide by zero",
            2:"You have entered incorrect expression"
        },
        "Windows":{
            0:"Settings",
            1:"Add account",
            2:"Rename account",
            3:"Delete account",
            4:"Statistics"
        }   
    },
    "Українська":{
        "Months":{
            1:"Січень",
            2:"Лютий",
            3:"Березень",
            4:"Квітень",
            5:"Травень",
            6:"Червень",
            7:"Липень",
            8:"Серпень",
            9:"Вересень",
            10:"Жовтень",
            11:"Листопад",
            12:"Грудень"
        },
        "General management":{
            0:"Видалити",
            1:"Додати",
            2:"Переназвати",
            3:"Ок",
            4:"Скасувати",
            5:"Обновити"
        },
        "Account":{
            0:"Ім'я",
            1:"Прізвище",
            2:"Поточний баланс",
            "Account management":{
                0:"Видалити акаунт",
                1:"Створити акаунт",
                2:"Переназвати акаунт",
                3:"Нове ім'я",
                4:"Нове Прізвище",
                "Messages":{
                    0:"Введіть ім'я і прізвище, щоб створити новий акаунт. (Використовувати те саме ім'я і призвище не можна) ",
                    1:"Введіть ім'я і прізвище акаунта, якого бажаєте видалити. ",
                    2:"Введіть нове ім'я і прізвище акаунта, щоб його переназвати. "
                }
            },
            "Info":{
                0:"Назва",
                1:"Дата",
                2:"Значення",
                3:"Баланс ",
                4:"Доходи",
                5:"Витрати",
                6:"Загалом: ",
                7:"Загальний дохід: ",
                8:"Загальні витрати: ",
                9:"Акаунт створенний ",
                "Statistics":{
                    0:"Статистика",
                    1:"Місячна",
                    2:"Квартальна",
                    3:"Річна",
                    4:"Загальний дохід ",
                    5:"Середній дохід ",
                    6:"Загальні витрати ",
                    7:"Середні витрати ",
                    8:"Дохід з витратами ",
                    9:"Найприбутковіша категорія ",
                    10:"Найприбутковіші категорії",
                    11:"Найприбутковіші транзакції:",
                    12:"Без назви",
                    13:"Найменш прибуткова категорія ",
                    14:"Найменш прибуткові категорії ",
                    15:"Найменш прибуткові транзакції:",
                    16:"Категорія ",
                    17:"Найдорожча категорія ",
                    18:"Найдорожчі категорії ",
                    19:"Найдорожчі транзакції ",
                    20:"Найдешевша категорія ",
                    21:"Найдешевші категорії ",
                    22:"Найдешевші транзакції ",
                }
            },
            "Transactions management":{
                0:"Додати транзакцію",
                1:"Видалити транзакцію",
                2:"Змінити транзакцію",
                "Messages":{
                    0:"Ведіть значення, які хочете змінити",
                    1:"""
                    Введіть назву (необов'язково) день і значення транзації за прикладом:

                                            Гарі Потер   28     13850
                                            Зарплата     20     25000
                    """
                }
            },
            "Category management":{
                0:"Додати категорію",
                1:"Видалити категорію",
                2:"Переназвати категорію",
                4:"Нова назва"
            }
        },
        "Errors":{
            0:"Ви ввели не правильний тип даних, перевірте їх знов",
            1:"Акаунт під такою назвою вже існує",
            2:"Ви не ввели поточного балансу, я зарахую це як 0 (якщо це не є правдим значенням, можуть виникнути розбіжності з реальним і поточним балансом). Продовжити?",
            3:"Ця категорія вже існує",
            4:"Ви впевненні що хочете видалити категорію? Ви втратите ВСІ транзакції, які були записані до цієї категорії і поточний баланс буде перерахований",
            5:"Виберіть транзакцію. (Щоб вибрати транзацію натисніть на її номер)",
            6:"Виберіть тільки одну транзакцію.",
            7:"Не можна залишати поля  пустими",
            8:"День мусить бути в діапазоні ",
            9:"Ви впевнені, що хочете видалити цю транзацію?",
            10:"Бажаєте загрузити account ?",
            11:"Ви впевнені, що хочете видалити account ? Ця дія є незворотньою",
            12:"Я не можу обрахувати пустий вираз",
            13:"Ви використали заборонені слова в виразі",
            14:"Ви повині мати принаймні одну категорію для доходів і одну для витрат, щоб побачити місячну статистику",
            15:"Ви повині мати принаймні одну тразакцію доходу і одні витрат, щоб побачити місячну статистику"

        },
        "Mini calculator":{
            0:"Міні калькулятор",
            1:"Не можна ділити на нуль",
            2:"Не правильно написаний вираз"
        },
        "Windows":{
            0:"Налаштування",
            1:"Додати акаунт",
            2:"Переназвати акаунт",
            3:"Видалити акаунт",
            4:"Статистика"
        }
    }
}


def change_language(Language,Categories:dict,Current_balance:int|float,Current_month:int,account:Account):
    Main_window.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(Current_balance))
    Main_window.current_month.setText(LANGUAGES[Language]["Months"][Current_month])
    Main_window.Incomes_and_expenses.setTabText(0,LANGUAGES[Language]["Account"]["Info"][4])
    Main_window.Incomes_and_expenses.setTabText(1,LANGUAGES[Language]["Account"]["Info"][5])
    Main_window.add_incomes_category.setText(LANGUAGES[Language]["Account"]["Category management"][0])
    Main_window.add_expenses_category.setText(LANGUAGES[Language]["Account"]["Category management"][0])
    Main_window.statistics.setText(LANGUAGES[Language]["Account"]["Info"]["Statistics"][0])
    Main_window.mini_calculator_label.setText(LANGUAGES[Language]["Mini calculator"][0])

    Settings_window.window.setWindowTitle(LANGUAGES[Language]["Windows"][0])
    Settings_window.delete_account.setText(LANGUAGES[Language]["Account"]["Account management"][0])
    Settings_window.add_account.setText(LANGUAGES[Language]["Account"]["Account management"][1])
    Settings_window.rename_account.setText(LANGUAGES[Language]["Account"]["Account management"][2])

    Rename_account_window.message.setText(LANGUAGES[Language]["Account"]["Account management"]["Messages"][1])
    Rename_account_window.button.setText(LANGUAGES[Language]["General management"][5])
    Rename_account_window.new_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Account management"][3])
    Rename_account_window.new_surname.setPlaceholderText(LANGUAGES[Language]["Account"]["Account management"][4])
    Rename_account_window.window.setWindowTitle(LANGUAGES[Language]["Windows"][2])

    Add_category_window.category_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][0])
    Add_category_window.button.setText(LANGUAGES[Language]["General management"][1])
    Add_category_window.window.setWindowTitle(LANGUAGES[Language]["Account"]["Category management"][0])

    Category_settings_window.delete_category.setText(LANGUAGES[Language]["Account"]["Category management"][1])
    Category_settings_window.rename_category.setText(LANGUAGES[Language]["Account"]["Category management"][2])

    Rename_category_window.new_category_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Category management"][4])
    Rename_category_window.button.setText(LANGUAGES[Language]["General management"][2])

    Transaction_management_window.button.setText(LANGUAGES[Language]["General management"][5])
    Transaction_management_window.transaction_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][0])
    Transaction_management_window.transaction_day.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][1])
    Transaction_management_window.transaction_value.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][2])

    Statistcs_window.window.setWindowTitle(LANGUAGES[Language]["Windows"][4])
    Statistcs_window.monthly_statistics.setText(LANGUAGES[Language]["Account"]["Info"]["Statistics"][1])
    Statistcs_window.quarterly_statistics.setText(LANGUAGES[Language]["Account"]["Info"]["Statistics"][2])
    Statistcs_window.yearly_statistics.setText(LANGUAGES[Language]["Account"]["Info"]["Statistics"][3])

    for index,error in enumerate(errors_list):
        error.setText(LANGUAGES[Language]["Errors"][index])
        error.button(QMessageBox.StandardButton.Ok).setText(LANGUAGES[Language]["General management"][3])
        if error.button(QMessageBox.StandardButton.Cancel) != None:
            error.button(QMessageBox.StandardButton.Cancel).setText(LANGUAGES[Language]["General management"][4])
    
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