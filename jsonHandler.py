import json


def get_top_level_keys(json_file="db.json"):
    with open(json_file) as file:
        return list(json.load(file).keys())


def delete_key(_key, json_file="db.json"):
    with open(json_file) as file:
        data = json.load(file)

    if _key in data:
        del data[_key]

    with open(json_file, "w") as file:
        json.dump(data, file, indent=2)
