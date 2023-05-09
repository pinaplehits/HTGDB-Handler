import os
import csv
from jsonHandler import write_to_child, get_top_level_keys, sort_json


def get_extensions(_items):
    return sorted(
        {
            os.path.splitext(os.path.basename(item[1]))[1].lower()
            for item in _items
            if " " not in os.path.splitext(os.path.basename(item[1]))[1]
        }
    )


def get_number_of_items(_file):
    with open(_file) as f:
        return sum(1 for line in f)


def get_txt_files(_path):
    return [
        os.path.join(_path, x)
        for x in os.listdir(_path)
        if os.path.splitext(x)[1].lower() == ".txt"
    ]


def read_file(_path, _delimiter="\t", _newline=""):
    _path = os.path.normpath(_path)
    with open(_path, newline=_newline) as file:
        return list(csv.reader(file, delimiter=_delimiter))


def reduced_smdb(_path="Reduced SMDBs/"):
    _path = os.path.normpath(_path)
    json_db = get_top_level_keys()

    smdb = get_txt_files(_path)

    for file in smdb:
        basename = os.path.splitext(os.path.basename(file))[0]
        if basename in json_db:
            data = read_file(file)

            write_to_child(basename, "reducedTo", get_number_of_items(file))
            write_to_child(basename, "extensions", get_extensions(data))


def original_smdb(_path="Hardware-Target-Game-Database/EverDrive Pack SMDBs/"):
    _path = os.path.normpath(_path)
    json_db = get_top_level_keys()

    smdb = get_txt_files(_path)

    for file in smdb:
        basename = os.path.splitext(os.path.basename(file))[0]
        if basename in json_db:
            write_to_child(basename, "reducedFrom", get_number_of_items(file))


if __name__ == "__main__":
    reduced_smdb()
    original_smdb()
    sort_json()
