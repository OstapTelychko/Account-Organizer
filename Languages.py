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
                    1:"Enter new name and surname. "
                }
            },
            "Info":{
                0:"Name",
                1:"Date",
                2:"Value",
                3:"Balance ",
                4:"Incomes",
                5:"Expenses",
                6:"Total ",
                7:"Total income: ",
                8:"Total expense: ",
                9:"Created ",
                "Statistics":{
                    0:"Statistics",
                    1:"Monthly",
                    2:"Quarterly",
                    3:"Yearly",
                    4:"Total income   ",
                    5:"Average income   ",
                    6:"Total expenses   ",
                    7:"Average expenses   ",
                    8:"Income with expenses   ",
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
                    23:" Quarter",
                    24:"Average income per day   ",
                    25:"Average income per month   ",
                    26:"Average expenses per day   ",
                    27:"Average expenses per month   ",
                    28:"Copy monthly statistics",
                    29:"Monthly statistics has copied",
                    30:"Copy quarterly statistics",
                    31:"Quarterly statistics has copied",
                    32:"Copy yearly statistics",
                    33:"Yearly statistics has copied"

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
                3:"New name",
                4:"Copy month transactions",
                5:"Month transactions have copied",
                6:"Name of category has updated",
                7:"Category has removed",
                8:"Category has created"
            }
        },
        "Errors":{
            0:"You have entered invalid type of data, check entered fields again",
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
            15:"You should have at least one income transaction and one expense transaction to see monthly statistics",
            16:"Name of category can't be empty field"
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
            4:"Statistics",
            5:"Quarterly Statistics",
            6:"Yearly statistics"
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
            5:"Оновити"
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
                    0:"Введіть ім'я і прізвище, щоб створити новий акаунт. (Використовувати те саме ім'я і прізвище не можна) ",
                    1:"Введіть нове ім'я і прізвище. "
                }
            },
            "Info":{
                0:"Назва",
                1:"Дата",
                2:"Значення",
                3:"Баланс ",
                4:"Доходи",
                5:"Витрати",
                6:"Загалом ",
                7:"Загальний дохід: ",
                8:"Загальні витрати: ",
                9:"Акаунт створенний ",
                "Statistics":{
                    0:"Статистика",
                    1:"Місячна",
                    2:"Квартальна",
                    3:"Річна",
                    4:"Загальний дохід   ",
                    5:"Середній дохід   ",
                    6:"Загальні витрати   ",
                    7:"Середні витрати   ",
                    8:"Дохід з витратами   ",
                    9:"Найприбутковіша категорія  ",
                    10:"Найприбутковіші категорії ",
                    11:"Найприбутковіші транзакції:",
                    12:"Без назви",
                    13:"Найменш прибуткова категорія  ",
                    14:"Найменш прибуткові категорії  ",
                    15:"Найменш прибуткові транзакції:",
                    16:"Категорія ",
                    17:"Найдорожча категорія  ",
                    18:"Найдорожчі категорії  ",
                    19:"Найдорожчі транзакції ",
                    20:"Найдешевша категорія  ",
                    21:"Найдешевші категорії  ",
                    22:"Найдешевші транзакції  ",
                    23:" Квартал",
                    24:"Середній дохід за день   ",
                    25:"Середній дохід за місяць   ",
                    26:"Середні витрати за день   ",
                    27:"Середні витрати за місяць   ",
                    28:"Скопіювати місячну статистику",
                    29:"Місячна статиска скопійована",
                    30:"Скопіювати квартальну статистику",
                    31:"Квартальна статистика скопійована",
                    32:"Скопіювати річну статистику",
                    33:"Річна статистика скопійована"
                }
            },
            "Transactions management":{
                0:"Додати транзакцію",
                1:"Видалити транзакцію",
                2:"Змінити транзакцію",
                "Messages":{
                    0:"Ведіть дані в поля, які хочете змінити",
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
                3:"Нова назва",
                4:"Скопіювати місячні транзакції",
                5:"Місячні транзакції скопійовані",
                6:"Назва категорії обновлена",
                7:"Категорія видалена",
                8:"Категорія створена"
            }
        },
        "Errors":{
            0:"Ви ввели не правильний тип даних, перевірте введені дані знов",
            1:"Акаунт під такою назвою вже існує",
            2:"Ви не ввели поточного балансу, я зарахую це як 0 (якщо це не є правдим значенням, можуть виникнути розбіжності з реальним і поточним балансом). Продовжити?",
            3:"Ця категорія вже існує",
            4:"Ви впевненні що хочете видалити категорію? Ви втратите ВСІ транзакції, які були записані до цієї категорії і поточний баланс буде перерахований",
            5:"Виберіть транзакцію. (Щоб вибрати транзацію натисніть на її номер)",
            6:"Виберіть тільки одну транзакцію.",
            7:"Не можна залишати поля  пустими",
            8:"День мусить бути в діапазоні ",
            9:"Ви впевнені, що хочете видалити цю транзакцію?",
            10:"Бажаєте загрузити account ?",
            11:"Ви впевнені, що хочете видалити account ? Ця дія є незворотньою",
            12:"Я не можу обрахувати пустий вираз",
            13:"Ви використали заборонені слова в виразі",
            14:"Ви повині мати принаймні одну категорію для доходів і одну для витрат, щоб побачити місячну статистику",
            15:"Ви повині мати принаймні одну тразакцію доходу і одну витрат, щоб побачити місячну статистику",
            16:"Назвою категорії не може бути пусте поле"
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
            4:"Статистика",
            5:"Квартальна статистика",
            6:"Річна статистика"
        }
    },
    "Polski":{
        "Months":{
            1:"Styczeń",
            2:"Luty",
            3:"Marzec",
            4:"Kwieсień",
            5:"Maj",
            6:"Czerwiec",
            7:"Lipiec",
            8:"Sierpień",
            9:"Wrzesień",
            10:"Październik",
            11:"Listopad",
            12:"Grudzień",
        },
        "General management":{
            0:"Usunąnć",
            1:"Dodać",
            2:"Zmienić nazwę",
            3:"Ok",
            4:"Anulować",
            5:"Zmienić"
        },
        "Account":{
            0:"Imię",
            1:"Nazwisko",
            2:"Potoczne saldo",
            "Account management":{
                0:"Usuń konto",
                1:"Dodaj konto",
                2:"Zmień nazwę konta",
                3:"Nowe imię",
                4:"Nowe nazwisko",
                "Messages":{
                    0:"Wprowadźcie imię i nazwisko, aby dodać nowe konto. (Nie wolno używać tego samego imienia i nazwiska)",
                    1:"Wprowadź nowe imię i nazwisko"
                }
            },
            "Info":{
                0:"Nazwa",
                1:"Data",
                2:"Wartość",
                3:"Saldo ",
                4:"Dochód ",
                5:"Wydatki ",
                6:"Ogólnie ",
                7:"Całkowity dochód: ",
                8:"Całkowite wydatki: ",
                9:"Konto dodane ",
                "Statistics":{
                    0:"Statystyka",
                    1:"Miesiączna",
                    2:"Kwartalna",
                    3:"Roczna",
                    4:"Całkowity dochód   ",
                    5:"Średni dochód   ",
                    6:"Całkowite wydatki   ",
                    7:"Średnie wydatki   ",
                    8:"Dochód z wydatkami   ",
                    9:"Najwięcej dochodów otrzymano z  ",
                    10:"Najwięcej dochodów otrzymano z  ",
                    11:"Najwiekszy dochód otrzymano z transakcji:  ",
                    12:"Bez nazwy ",
                    13:"Najmniej dochodów otrzymano z  ",
                    14:"Najmniej dochodów otrzymano z  ",
                    15:"Najmniejszy dochód otrzymano z transakcji:  ",
                    16:"Kategoria ",
                    17:"Najdroższa kategoria  ",
                    18:"Najdroższe kategorie  ",
                    19:"Najdroższe transakcji  ",
                    20:"Najtańsza kategoria  ",
                    21:"Najtańsze kategorie  ",
                    22:"Najtańsze transakcji  ",
                    23:" Kwartał",
                    24:"Średni dzienny dochód  ",
                    25:"Średni miesięczny dochód  ",
                    26:"Średnie wytraty dziennie  ",
                    27:"Średnie wytraty miesięczne  ",
                    28:"Kopiować miesięczną statystykę",
                    29:"Miesięczna statystyka skopiowana",
                    30:"Kopiować kwartalną statystykę",
                    31:"Kwartalna statystyka skopiowana",
                    32:"Kopiować roczną statystykę",
                    33:"Roczna statystyka skopiowana"
                }  
            },
            "Transactions management":{
                0:"Dodać transakcję",
                1:"Usunąć transakcję",
                2:"Źmienić transakcję",
                "Messages":{
                    0:"Wprowadźcie dane w polach, które chcecie zmienić",
                    1:"""
                    Wpiszcie nazwę (niekonicznie), dzień i wartość transakcji za przykładem:

                                            Harry'ego Pottera   28    13850
                                            Wypłata         20      25000
                    """
                }
            },
            "Category management":{
                0:"Dodać kategorię",
                1:"Usunąć kategorię",
                2:"Zmienić nazwę kategorii",
                3:"Nowa nazwa",
                4:"Kopiować miesięczne transakcje",
                5:"Miesięczne transakcje są skopiowane",
                6:"Nazwa kategorii zmieniona",
                7:"Kategoria usunięta",
                8:"Kategoria dodana"
            }
        },
        "Errors":{
            0:"Wpisaliscie nie korektny typ danych, sprawdź wpisane dane znow",
            1:"Konto z takim imieniem już istnieje",
            2:"Nie podałeś aktualnego salda, policzę to jako 0 (jeśli to nieprawda, wystąpi rozbieżność między rzeczywistym a całkowitym saldem). Kontynuować?",
            3:"Ta kategoria już istnieje",
            4:"Czy na pewno chcecie usunąć kategorię? Utracisz WSZYSTKIE transakcje zarejestrowane w tej kategorii, a bieżące saldo zostanie przeliczone",
            5:"Wybierzcie transakcję. (aby wybrać transakcję, kliknij na jej numer)",
            6:"Wybierzcie tylko jedną transakcję.",
            7:"Pola nie mogą pozostać puste",
            8:"Dzień powinien być w zakresie ",
            9:"Czy na pewno chcecie usunąć tę transakcję?",
            10:"Załadować account ?",
            11:"Czy na pewno chcecie usunąć account ? Ta czynność jest nieodwracalna",
            12:"Nie mogę obliczyć pustego wyrażenia",
            13:"W wyrażeniu użyłeś zabronionych słów",
            14:"Aby zobaczyć statystyki miesięczne, musisz mieć co najmniej jedną kategorię dochodów i jedną kategorię wydatków",
            15:"Aby zobaczyć miesięczne statystyki, musisz mieć co najmniej jedną transakcję dochodu i jedną transakcję wydatkóws",
            16:"Nazwą kategorii nie morze być puste pole"
        },
        "Mini calculator":{
            0:"Mały kalkulator",
            1:"Nie można podzielić przez zero",
            2:"Wyrażenie jest napisane nie poprawnie"
        },
        "Windows":{
            0:"Ustawienia",
            1:"Dodać konto",
            2:"Zmienić nazwę konta",
            3:"Usunąnć konto",
            4:"Statystyka",
            5:"Statystyka kwartalna",
            6:"Statystyka roczna"
        }
    }
}



def change_language(Language, Categories:dict, Current_balance:int|float, Current_month:int, account:Account):

    MainWindow.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(Current_balance))
    MainWindow.current_month.setText(LANGUAGES[Language]["Months"][Current_month])
    MainWindow.Incomes_and_expenses.setTabText(0,LANGUAGES[Language]["Account"]["Info"][4])
    MainWindow.Incomes_and_expenses.setTabText(1,LANGUAGES[Language]["Account"]["Info"][5])
    MainWindow.add_incomes_category.setText(LANGUAGES[Language]["Account"]["Category management"][0])
    MainWindow.add_expenses_category.setText(LANGUAGES[Language]["Account"]["Category management"][0])
    MainWindow.statistics.setText(LANGUAGES[Language]["Account"]["Info"]["Statistics"][0])
    MainWindow.mini_calculator_label.setText(LANGUAGES[Language]["Mini calculator"][0])

    SettingsWindow.window.setWindowTitle(LANGUAGES[Language]["Windows"][0])
    SettingsWindow.delete_account.setText(LANGUAGES[Language]["Account"]["Account management"][0])
    SettingsWindow.add_account.setText(LANGUAGES[Language]["Account"]["Account management"][1])
    SettingsWindow.rename_account.setText(LANGUAGES[Language]["Account"]["Account management"][2])

    RenameAccountWindow.message.setText(LANGUAGES[Language]["Account"]["Account management"]["Messages"][1])
    RenameAccountWindow.button.setText(LANGUAGES[Language]["General management"][5])
    RenameAccountWindow.new_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Account management"][3])
    RenameAccountWindow.new_surname.setPlaceholderText(LANGUAGES[Language]["Account"]["Account management"][4])
    RenameAccountWindow.window.setWindowTitle(LANGUAGES[Language]["Windows"][2])

    AddCategoryWindow.category_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][0])
    AddCategoryWindow.button.setText(LANGUAGES[Language]["General management"][1])
    AddCategoryWindow.window.setWindowTitle(LANGUAGES[Language]["Account"]["Category management"][0])

    CategorySettingsWindow.delete_category.setText(LANGUAGES[Language]["Account"]["Category management"][1])
    CategorySettingsWindow.rename_category.setText(LANGUAGES[Language]["Account"]["Category management"][2])
    CategorySettingsWindow.copy_transactions.setText(LANGUAGES[Language]["Account"]["Category management"][4])

    RenameCategoryWindow.new_category_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Category management"][3])
    RenameCategoryWindow.button.setText(LANGUAGES[Language]["General management"][2])

    TransactionManagementWindow.button.setText(LANGUAGES[Language]["General management"][5])
    TransactionManagementWindow.transaction_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][0])
    TransactionManagementWindow.transaction_day.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][1])
    TransactionManagementWindow.transaction_value.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][2])

    StatistcsWindow.window.setWindowTitle(LANGUAGES[Language]["Windows"][4])
    StatistcsWindow.monthly_statistics.setText(LANGUAGES[Language]["Account"]["Info"]["Statistics"][1])
    StatistcsWindow.quarterly_statistics.setText(LANGUAGES[Language]["Account"]["Info"]["Statistics"][2])
    StatistcsWindow.yearly_statistics.setText(LANGUAGES[Language]["Account"]["Info"]["Statistics"][3])

    MonthlyStatistics.copy_statistics.setText(LANGUAGES[Language]["Account"]["Info"]["Statistics"][28])

    QuarterlyStatistics.window.setWindowTitle(LANGUAGES[Language]["Windows"][5])
    QuarterlyStatistics.copy_statistics.setText(LANGUAGES[Language]["Account"]["Info"]["Statistics"][30])
    quarters_numbers = ["I","II","III","IV"]
    month_number = 1
    for quarter in QuarterlyStatistics.statistics:
        QuarterlyStatistics.statistics[quarter]["Label"].setText(quarters_numbers[quarter-1]+LANGUAGES[Language]["Account"]["Info"]["Statistics"][23])
        for month_list in QuarterlyStatistics.statistics[quarter]:
            if month_list != 0 and month_list != "Label":
                QuarterlyStatistics.statistics[quarter][month_list]["Label"].setText(LANGUAGES[Language]["Months"][month_number])
                month_number+=1
            elif month_list == 0:
                QuarterlyStatistics.statistics[quarter][0]["Label"].setText(LANGUAGES[Language]["Account"]["Info"][6])
    
    YearlyStatistics.window.setWindowTitle(LANGUAGES[Language]["Windows"][6])
    YearlyStatistics.copy_statistics.setText(LANGUAGES[Language]["Account"]["Info"]["Statistics"][32])
    for month_list in YearlyStatistics.statistics:
        if month_list != 0:
            YearlyStatistics.statistics[month_list]["Label"].setText(LANGUAGES[Language]["Months"][month_list])
        else:
            YearlyStatistics.statistics[0]["Label"].setText(LANGUAGES[Language]["Account"]["Info"][6])


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
    
    MainWindow.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(Current_balance))
    Incomes = SettingsWindow.total_income.text().split(" ")[2]
    SettingsWindow.total_income.setText(LANGUAGES[Language]["Account"]["Info"][7]+str(Incomes))
    Expenses = SettingsWindow.total_expense.text().split(" ")[2]
    SettingsWindow.total_expense.setText(LANGUAGES[Language]["Account"]["Info"][8]+str(Expenses))
    SettingsWindow.account_created_date.setText(LANGUAGES[Language]["Account"]["Info"][9]+account.get_account_date())  