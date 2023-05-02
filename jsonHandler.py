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
