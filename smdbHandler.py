from jsonHandler import write_to_child, get_top_level_keys
import csv
import os


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


def get_all_smdb(_path):
    smdb = sorted([x for x in os.listdir(_path) if x.endswith(".txt")], key=str.lower)
    basename = [os.path.splitext(os.path.basename(x))[0] for x in smdb]

    return smdb, basename


def read_file(_path, _delimiter="\t", _newline=""):
    _path = os.path.normpath(_path)
    with open(_path, newline=_newline) as f:
        return list(csv.reader(f, delimiter=_delimiter))


def read_missing_file(_path):
    _path = os.path.normpath(_path)
    basename = os.path.splitext(os.path.basename(_path))[0]

    if basename not in get_top_level_keys():
        return

    with open(_path, "r") as f:
        missing_data = list(csv.reader(f, delimiter="\t"))
        write_to_child(basename, "missing", missing_data)


def reduced_master(_path="Reduced SMDBs/"):
    smdb = get_txt_files(_path)
    data = [line for file in smdb for line in read_file(file)]

    dataset = set([item[0] for item in data])

    newdb = [
        item for item in data if item[0] in dataset and dataset.remove(item[0]) is None
    ]

    return newdb


def reduced_smdb(_path="Reduced SMDBs/"):
    _path = os.path.normpath(_path)
    json_db = get_top_level_keys()
    smdb = get_txt_files(_path)

    len_reduced = 0

    for file in smdb:
        len_smdb = get_number_of_items(file)
        len_reduced += len_smdb
        # continue
        basename = os.path.splitext(os.path.basename(file))[0]

        if basename in json_db:
            data = read_file(file)

            write_to_child(basename, "reducedTo", len_smdb)
            write_to_child(basename, "extensions", get_extensions(data))

    return len_reduced


def original_smdb(_path="Hardware-Target-Game-Database/EverDrive Pack SMDBs/"):
    _path = os.path.normpath(_path)
    json_db = get_top_level_keys()
    smdb = get_txt_files(_path)

    len_original = 0

    for file in smdb:
        len_smdb = get_number_of_items(file)
        len_original += len_smdb
        # continue
        basename = os.path.splitext(os.path.basename(file))[0]

        if basename in json_db:
            write_to_child(basename, "reducedFrom", len_smdb)

    return len_original


if __name__ == "__main__":
    # print(reduced_smdb())
    # print(original_smdb() - reduced_smdb())

    # read_missing_file("D:\\MegaSD SMDB.txt")
    reduced_master()
