from __future__ import annotations
from typing import TypeAlias, cast, Union
import json
from project_configuration import APP_DIRECTORY


with open(f"{APP_DIRECTORY}/languages.json", encoding="utf-8") as file:
    languages_data = json.load(file)

RawTranslationCategory:TypeAlias = dict[str, Union[str, "RawTranslationCategory"]]
ParsedTranslationCategory:TypeAlias = dict[str|int, Union["ParsedTranslationCategory", str]]
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
