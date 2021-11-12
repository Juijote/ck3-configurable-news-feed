import os
import pathlib
import ruamel.yaml
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

non_english_languages = [
    'french',
    'german',
    'korean',
    'russian',
    'simp_chinese',
    'spanish',
]

def get_all_localization(language):
    localization = {}

    root = os.path.join('.', 'localization', language)

    for filename in os.listdir(root):
        if not os.path.isfile(os.path.join(root, filename)):
            continue

        if 'generated' in filename:
            continue

        category = filename.removeprefix('newsfeed_').removesuffix('_l_english.yml')
        filepath = os.path.join(root, filename)
        
        with open(filepath, 'r', encoding='utf-8-sig') as file:
            yaml = ruamel.yaml.YAML()
            doc = yaml.load(file)
            localization[category] = doc[f"l_{language}"]

    return localization

def get_localization_by_category(language, category):
    filepath = os.path.join('.', 'localization', language, f'newsfeed_{category}_l_{language}.yml')

    try:
        with open(filepath, 'r', encoding='utf-8-sig') as file:
            yaml = ruamel.yaml.YAML()
            doc = yaml.load(file)
            return doc[f"l_{language}"]
    except FileNotFoundError:
        return {}

def generate_localization():
    all_english_loc = get_all_localization('english')

    for language in non_english_languages:
        missing_keys = []

        for category, english_loc in all_english_loc.items():
            language_dir = os.path.join('.', 'localization', language)
            generated_dir = os.path.join(language_dir, 'generated')
            generated_path = os.path.join(generated_dir, f"newsfeed_{category}_generated_l_{language}.yml")

            language_loc = get_localization_by_category(language, category)

            missing_keys = [key for key in english_loc.keys() if key not in language_loc]

            if missing_keys:
                generated_dict = {f"l_{language}": {key: DoubleQuotedScalarString(english_loc[key]) for key in missing_keys}}

                pathlib.Path(generated_dir).mkdir(parents=True, exist_ok=True)

                with open(generated_path, 'w', encoding='utf-8-sig') as file:
                    yaml = ruamel.yaml.YAML()
                    yaml.width = 4096
                    yaml.dump(generated_dict, file)
            else:
                try:
                    pathlib.Path(generated_path).unlink()
                except FileNotFoundError:
                    pass

generate_localization()