import json
from project_configuration import ROOT_DIRECTORY

with open(f"{ROOT_DIRECTORY}/languages.json") as file:
    languages_data = json.load(file)

def convert_digit_keys_to_int(obj):
    new_translation_category = {}
    for key, value in obj.items():
        if key.isdigit():
            new_translation_category[int(key)] = value
        else:
            new_translation_category[key] = convert_digit_keys_to_int(value)
    return new_translation_category

LANGUAGES = convert_digit_keys_to_int(languages_data)
