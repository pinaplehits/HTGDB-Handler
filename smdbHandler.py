from jsonHandler import read_from_child
import csv
import os


def get_smdb_with_missing(_json_keys, _json_file="db.json"):
    return [key for key in _json_keys if read_from_child(key, "missing", _json_file)]


def get_smdb_not_verified(_sha1, _json_keys, _json_file="db.json"):
    return [
        key
        for key in _json_keys
        if (verified := read_from_child(key, "verifiedWith", _json_file)) != _sha1
        or not verified
    ]


def get_extensions(_items):
    return sorted(
        {
            os.path.splitext(os.path.basename(item[1]))[1].lower()
            for item in _items
            if " " not in os.path.splitext(os.path.basename(item[1]))[1]
        }
    )


def get_number_of_items(_path):
    with open(_path) as file:
        return sum(1 for line in file)


def get_files_with_extension(_path, _extension=".txt"):
    return [
        os.path.join(_path, file)
        for file in os.listdir(_path)
        if os.path.splitext(file)[1].lower() == _extension
    ]


def get_all_smdb(_path, _extension=".txt"):
    smdb = sorted(
        [file for file in os.listdir(_path) if file.endswith(_extension)], key=str.lower
    )
    basename = [os.path.splitext(os.path.basename(file))[0] for file in smdb]

    return smdb, basename


def read_file(_path, _delimiter="\t", _newline=""):
    _path = os.path.normpath(_path)
    with open(_path, newline=_newline) as file:
        return list(csv.reader(file, delimiter=_delimiter))


def create_new_file(_path, _data, _delimiter="\t"):
    print(f"Creating {os.path.basename(_path)} file...")

    with open(_path, "w", newline="") as f:
        csv.writer(f, delimiter=_delimiter).writerows(_data)

    print(f"File {os.path.basename(_path)} is created")


def reduced_master(_path="Reduced SMDBs/"):
    data = combine_all_smdb(_path)
    dataset = set([item[0] for item in data])

    newdb = [
        item for item in data if item[0] in dataset and dataset.remove(item[0]) is None
    ]

    return newdb


def combine_all_smdb(_path="Reduced SMDBs/"):
    smdb = get_files_with_extension(_path)
    return [line for file in smdb for line in read_file(file)]
