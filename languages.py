from __future__ import annotations
import json
from typing import TypeAlias, cast, Union
from operator import getitem
from functools import reduce

from AppObjects.session import Session
from AppObjects.logger import get_logger
from project_configuration import APP_DIRECTORY


logger = get_logger(__name__)

class LanguageCategory:
    """This class is used to create a tree structure for the language categories.

        Usage
        -----
        >>> Main = LanguageCategory("Main")
        >>> Subcategory = Main.add_subcategory("Subcategory")
        >>> Subcategory.path()
        ['Main', 'Subcategory']"""


    def __init__(self, name:str, parent:LanguageCategory|None = None):
        self.name = name
        self.parent = parent
        self._children:dict[str, LanguageCategory] = {}
    

    def path(self) -> list[str]:
        node = self
        path:list[str] = []

        while node:
            path.insert(0, node.name)
            node = node.parent
        return path


    def add_subcategory(self, name:str) -> LanguageCategory:
        if name not in self._children:
            subcategory = LanguageCategory(name, self)
            self._children[name] = subcategory

            return subcategory
    

    def get_translation(self, translation_index:int) -> str:
        """Get the translation for the category. If the translation is not found, return the name of the category."""
        
        try:
            translations_category = reduce(getitem, self.path(), LANGUAGES[Session.language])
        except KeyError as exception:
            logger.error(f"{exception} - path: {self.path()} - language: {Session.language}")
        
        translation = translations_category.get(translation_index)
        if translation is None:
            logger.debug(f"Translation not found for {self.path()} - {translation_index}")

        return translation



class LanguageStructure():
    """This class is used to create a structure for the language categories. And simplify categories names maintenance.

        Usage
        -----
        >>> LanguageStructure.Months.path()
        ['Months']
        >>> LanguageStructure.MainWindow.path()
        ['Windows', 'Main']
        >>> LanguageStructure.Transactions.path()
        ['Windows', 'Main', 'Transactions']"""

    Months = LanguageCategory("Months")
    GeneralManagement = LanguageCategory("General management")

    Windows = LanguageCategory("Windows")

    MainWindow = Windows.add_subcategory("Main")
    Transactions = MainWindow.add_subcategory("Transactions")
    TransactionsMessages = Transactions.add_subcategory("Messages")
    Categories = MainWindow.add_subcategory("Categories")
    MiniCalculator = MainWindow.add_subcategory("Mini calculator")

    Settings = Windows.add_subcategory("Settings")
    BackupManagement = Settings.add_subcategory("Backup management")
    Account = Settings.add_subcategory("Account")
    AccountMessages = Account.add_subcategory("Messages")

    Statistics = Windows.add_subcategory("Statistics")
    Update = Windows.add_subcategory("Update")

    Messages = LanguageCategory("Messages")



with open(f"{APP_DIRECTORY}/languages.json", encoding="utf-8") as file:
    languages_data = json.load(file)

RawTranslationCategory:TypeAlias = dict[str, Union[str, "RawTranslationCategory"]]
ParsedTranslationCategory:TypeAlias = dict[int|str, Union[str, "ParsedTranslationCategory"]]
IntermediateTranslationCategory:TypeAlias = dict[int|str, str | RawTranslationCategory | ParsedTranslationCategory]

def convert_digit_keys_to_int(obj:RawTranslationCategory) -> ParsedTranslationCategory:
    """
    Convert digit keys in a dictionary to integers. It's necessary because json can't store keys as integers."""

    new_translation_category:IntermediateTranslationCategory = {}
    for key, value in obj.items():
        if not isinstance(value, dict):
            new_translation_category[int(key)] = value
        else:
            new_translation_category[key] = convert_digit_keys_to_int(value)

    return cast(ParsedTranslationCategory, new_translation_category)

LANGUAGES = convert_digit_keys_to_int(languages_data)
