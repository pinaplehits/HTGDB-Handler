import csv
import os
from jsonHandler import read_from_child
from typing import List


def get_smdb_with_missing_values(
    json_keys: List[str], json_file: str = "db.json"
) -> List[str]:
    return [key for key in json_keys if read_from_child(key, "missing", json_file)]


def get_smdb_not_verified(
    sha1: str, json_keys: List[str], json_file: str = "db.json"
) -> List[str]:
    return [
        key
        for key in json_keys
        if (verified := read_from_child(key, "verifiedWith", json_file)) != sha1
        or not verified
    ]


def find_matching_keys_in_smdb(
    json_keys: List[str], search_key: str, json_file: str = "db.json"
) -> List[str]:
    return [key for key in json_keys if read_from_child(key, search_key, json_file)]


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
    print(f"Creating {os.path.basename(path)} file...")

    with open(path, "w", newline="") as f:
        csv.writer(f, delimiter=delimiter).writerows(data)

    print(f"File {os.path.basename(path)} is created")


def reduced_master(path: str = "Reduced SMDBs/") -> List[List[str]]:
    data = combine_all_smdb(path)
    dataset = set([item[0] for item in data])

    return [
        item for item in data if item[0] in dataset and dataset.remove(item[0]) is None
    ]


def combine_all_smdb(path: str = "Reduced SMDBs/") -> List[List[str]]:
    smdb = get_files_with_extension(path)
    return [line for file in smdb for line in read_file(file)]
