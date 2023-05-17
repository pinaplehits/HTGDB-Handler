import json
import os


def get_top_level_keys(json_file="db.json"):
    try:
        with open(json_file) as f:
            return list(json.load(f).keys())
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")

    return []


def delete_key(_key, json_file="db.json"):
    try:
        with open(json_file) as f:
            data = json.load(f)

        try:
            data.pop(_key)
            print(f"Deleted {_key}")
        except KeyError:
            print(f"Couldn't delete {_key}. Key not found.")
            return

        with open(json_file, "w") as f:
            json.dump(data, f, indent=2)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")


def write_to_child(_basename, _child, _data, _json_db="db.json"):
    try:
        with open(_json_db, "r") as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")
        exit()

    try:
        json_data[_basename][_child] = _data
    except KeyError as e:
        print(f"Error {e} not found in the JSON file")
        exit()

    try:
        with open(_json_db, "w") as f:
            json.dump(json_data, f, indent=2)
    except IOError as e:
        print(f"Error writing to the JSON file: {e}")
        exit()


def read_from_child(_basename, _child, _json_db="db.json"):
    try:
        with open(_json_db, "r") as f:
            json_data = json.load(f)
            return json_data.get(_basename, {}).get(_child)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")

    return None


def read_from_key(_key, _json_db="db.json"):
    try:
        with open(_json_db, "r") as f:
            json_data = json.load(f)
            return json_data.get(_key)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")

    return None


def sort_json(_json_db="db.json"):
    try:
        with open(_json_db, "r") as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")
        return

    try:
        with open(_json_db, "w") as f:
            json.dump(json_data, f, indent=2, sort_keys=True)
    except IOError as e:
        print(f"Error writing to the JSON file: {e}")
        return


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
