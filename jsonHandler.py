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
        json.dump(data, file, indent=2)


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
        json.dump(json_data, f, indent=2)


def read_from_child(_basename, _child, _json_db="db.json"):
    try:
        with open(_json_db, "r") as f:
            json_data = json.load(f)
    except json.decoder.JSONDecodeError:
        print("JSON file is empty")
        return None

    return json_data.get(_basename, {}).get(_child)


def read_from_key(_key, _json_db="db.json"):
    try:
        with open(_json_db, "r") as f:
            json_data = json.load(f)

            if _key not in json_data:
                return None

            return json_data[_key]
    except json.decoder.JSONDecodeError:
        print("JSON file is empty")
        return None


def sort_json(_json_db="db.json"):
    with open(_json_db, "r") as f:
        json_data = json.load(f)

    with open(_json_db, "w") as f:
        json.dump(json_data, f, indent=2, sort_keys=True)


def missing_db():
    db = get_top_level_keys()

    if os.path.exists("missing.json"):
        os.remove("missing.json")

    with open("missing.json", "w") as f:
        json.dump({}, f)

    for key in db:
        missing = read_from_child(key, "missing")
        if missing:
            print(f"{key} is missing {len(missing)} items")
            write_to_child(key, "missing", missing, "missing.json")


if __name__ == "__main__":
    missing_db()
