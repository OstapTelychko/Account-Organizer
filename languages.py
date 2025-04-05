import json
from project_configuration import APP_DIRECTORY


with open(f"{APP_DIRECTORY}/languages.json", encoding="utf-8") as file:
    languages_data = json.load(file)

def convert_digit_keys_to_int(obj:dict[str, str]):
    """
    Convert digit keys in a dictionary to integers. It's necessary because json can't store keys as integers."""

    new_translation_category = {}
    for key, value in obj.items():
        if key.isdigit():
            new_translation_category[int(key)] = value
        else:
            new_translation_category[key] = convert_digit_keys_to_int(value)
    return new_translation_category

LANGUAGES = convert_digit_keys_to_int(languages_data)
