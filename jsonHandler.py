import json
import os


def get_top_level_keys(json_file: str = "db.json") -> list:
    try:
        with open(json_file) as f:
            return list(json.load(f).keys())
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")

    return []


def delete_key(key: str, json_file: str = "db.json") -> None:
    try:
        with open(json_file) as f:
            data = json.load(f)

        try:
            data.pop(key)
            print(f"Deleted {key}")
        except KeyError:
            print(f"Couldn't delete {key}. Key not found.")
            return

        with open(json_file, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")


def write_to_child(
    basename: str, child: str, data: dict, json_db: str = "db.json"
) -> None:
    try:
        with open(json_db, "r") as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")
        exit()

    try:
        json_data[basename][child] = data
    except KeyError as e:
        print(f"Error {e} not found in the JSON file")
        exit()

    try:
        with open(json_db, "w") as f:
            json.dump(json_data, f, indent=2, sort_keys=True)
    except IOError as e:
        print(f"Error writing to the JSON file: {e}")
        exit()


def update_json_with_dict(data: dict, json_db: str = "db.json") -> None:
    try:
        with open(json_db, "r") as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")
        exit()

    for key, value in data.items():
        if key in json_data:
            json_data[key].update(value)
        else:
            json_data[key] = value

    try:
        with open(json_db, "w") as f:
            json.dump(json_data, f, indent=2, sort_keys=True)
    except IOError as e:
        print(f"Error writing to the JSON file: {e}")
        exit()


def write_to_key(key: str, json_db: str = "db.json") -> None:
    try:
        with open(json_db, "r") as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")
        exit()

    json_data.setdefault(key, {})

    try:
        with open(json_db, "w") as f:
            json.dump(json_data, f, indent=2, sort_keys=True)
    except IOError as e:
        print(f"Error writing to the JSON file: {e}")
        exit()


def read_from_child(basename: str, child: str, json_db: str = "db.json") -> dict:
    try:
        with open(json_db, "r") as f:
            json_data = json.load(f)
            return json_data.get(basename, {}).get(child)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")
        return None


def read_from_key(key: str, json_db: str = "db.json") -> dict:
    try:
        with open(json_db, "r") as f:
            json_data = json.load(f)
            return json_data.get(key)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        print(f"Error reading the JSON file: {e}")
        return None


def create_json(json_db: str) -> None:
    if os.path.exists(json_db):
        os.remove(json_db)

    try:
        with open(json_db, "w") as f:
            json.dump({}, f)
    except IOError as e:
        print(f"Error writing to the JSON file: {e}")
        return


def create_json_from_child(json_db: str, child: str) -> None:
    create_json(json_db)

    print(f"Writing to {json_db}...")

    for key in get_top_level_keys():
        if item := read_from_child(key, child):
            write_to_key(key, json_db)
            write_to_child(key, child, item, json_db)

    print(f"Done writing to {json_db}.")


if __name__ == "__main__":
    create_json_from_child("missing.json", "missing")
    create_json_from_child("extensions.json", "extensions")
