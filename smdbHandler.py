import logging
import csv
import os
from jsonHandler import read_from_child, create_json
from typing import List
import json


def search_value_in_key(
    json_keys: List[str], search_key: str, search_value: str, json_file: str = "db.json"
) -> List[str]:
    return [
        key
        for key in json_keys
        if read_from_child(key, search_key, json_file) == search_value
    ]


def find_non_empty_key(
    json_keys: List[str], search_key: str, json_file: str = "db.json"
) -> List[str]:
    return [key for key in json_keys if read_from_child(key, search_key, json_file)]


def get_smdb_not_verified(
    sha1: str, json_keys: List[str], json_file: str = "db.json"
) -> List[str]:
    return [
        key
        for key in json_keys
        if (verified := read_from_child(key, "verifiedWith", json_file)) != sha1
        or not verified
    ]


def get_extensions(items: List[str]) -> List[str]:
    return sorted(
        {
            os.path.splitext(os.path.basename(item[1]))[1].lower()
            for item in items
            if " " not in os.path.splitext(os.path.basename(item[1]))[1]
        }
    )


def get_number_of_items(path: str) -> int:
    with open(path) as file:
        return sum(1 for line in file)


def get_files_with_extension(path: str, extension: str = ".txt") -> List[str]:
    return [
        os.path.join(path, file)
        for file in os.listdir(path)
        if os.path.splitext(file)[1].lower() == extension
    ]


def get_all_smdb_from_path(path: str, extension: str = ".txt") -> List[str]:
    return [file for file in os.listdir(path) if file.endswith(extension)]


def read_file(path: str, delimiter: str = "\t", newline: str = "") -> List[List[str]]:
    path = os.path.normpath(path)
    with open(path, newline=newline) as file:
        return list(csv.reader(file, delimiter=delimiter))


def create_new_file(path: str, data: List[List[str]], delimiter: str = "\t") -> None:
    logging.info(f"Creating {os.path.basename(path)} file...")

    try:
        with open(path, "w", newline="") as f:
            csv.writer(f, delimiter=delimiter).writerows(data)
    except IOError as e:
        logging.error(f"Failed to create {os.path.basename(path)}: {e}")
        return

    logging.info(f"File {os.path.basename(path)} is created")


def reduced_master(path: str = "Reduced SMDBs/") -> List[List[str]]:
    data = combine_all_smdb(path)
    dataset = set([item[0] for item in data])

    return [
        item for item in data if item[0] in dataset and dataset.remove(item[0]) is None
    ]


def combine_all_smdb(path: str = "Reduced SMDBs/") -> List[List[str]]:
    smdb = get_files_with_extension(path)
    return [line for file in smdb for line in read_file(file)]


def create_master():
    data = {}
    items = reduced_master()
    database = "master.json"

    create_json(database)

    for item in items:
        item_data = {
            "crc32": item[4],
            "md5": item[3],
            "paths": item[1],
            "sha1": item[2],
        }
        if len(item) > 5:
            item_data["size"] = item[5]
        data[item[0]] = item_data

    with open(database, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    create_master()
