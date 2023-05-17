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


def write_to_key(_key, _json_db="db.json"):
    try:
        with open(_json_db, "r") as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")
        exit()

    json_data.setdefault(_key, {})

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


def create_child_json(_json_db, _child):
    db = get_top_level_keys()

    if os.path.exists(_json_db):
        os.remove(_json_db)

    with open(_json_db, "w") as f:
        json.dump({}, f)

    print(f"Writing to {_json_db}...")
    for key in db:
        item = read_from_child(key, _child)
        if item:
            write_to_key(key, _json_db)
            write_to_child(key, _child, item, _json_db)
    print(f"Done writing to {_json_db}.")


if __name__ == "__main__":
    create_child_json("missing.json", "missing")
    create_child_json("extensions.json", "extensions")
