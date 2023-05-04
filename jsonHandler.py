import json
import os


def get_top_level_keys(json_file="db.json"):
    with open(json_file) as file:
        return list(json.load(file).keys())


def delete_key(_key, json_file="db.json"):
    with open(json_file) as file:
        data = json.load(file)

    if _key in data:
        del data[_key]

    with open(json_file, "w") as file:
        json.dump(data, file, indent=2, sort_keys=True)


def write_to_child(_basename, _child, _data, _json_db="db.json"):
    json_data = {}

    try:
        with open(_json_db, "r") as f:
            json_data = json.load(f)
    except json.decoder.JSONDecodeError:
        pass

    if _basename not in json_data:
        json_data[_basename] = {}

    json_data[_basename][_child] = _data

    with open(_json_db, "w") as f:
        json.dump(json_data, f, indent=2, sort_keys=True)


def read_from_child(_basename, _child, _json_db="db.json"):
    json_data = {}

    try:
        with open(_json_db, "r") as f:
            json_data = json.load(f)
    except json.decoder.JSONDecodeError:
        pass

    if _basename not in json_data:
        return {}

    if _child not in json_data[_basename]:
        return {}

    return json_data[_basename][_child]


def read_from_key(_key, _json_db="db.json"):
    json_data = {}

    try:
        with open(_json_db, "r") as f:
            json_data = json.load(f)
    except json.decoder.JSONDecodeError:
        pass

    if _key not in json_data:
        return {}

    return json_data[_key]


# def missing_db():
#     db = get_top_level_keys()

#     if not os.path.exists("missing.json"):
#         with open("missing.json", "w") as f:
#             json.dump({}, f)

#     for key in db:
#         missing = read_from_child(key, "missing")
#         if missing:
#             print(f"{key} is missing {len(missing)} items")
#             write_to_child(key, "missing", missing, "missing.json")


# missing_db()
