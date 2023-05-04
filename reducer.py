from configparser import ConfigParser
from gitHandler import update_repo, git_difference
from jsonHandler import get_top_level_keys, delete_key, write_to_child
import csv
import json
import os
import shutil


def load_config(_section="reducer", _file="config.ini"):
    config = ConfigParser()
    config.read(_file)

    return dict(config.items(_section))


def populate_list(_path):
    with open(str(_path), newline="") as file:
        return list(csv.reader(file, delimiter="\t"))


def get_extensions(_items):
    return sorted(
        set([os.path.splitext(os.path.basename(item[1]))[1].lower() for item in _items])
    )


def single_file_db(_items):
    dataset = set([item[0] for item in _items])

    if len(dataset) == len(_items):
        print("SMDB not reduced")
        return _items

    newdb = [
        item
        for item in _items
        if item[0] in dataset and dataset.remove(item[0]) is None
    ]

    print(f"SMDB reduced from {len(_items)} to {len(newdb)} files")

    return newdb


def new_file(_path, _delimiter, _data):
    print(f"Creating {os.path.basename(_path)} file...")

    with open(_path, "w", newline="") as file:
        csv.writer(file, delimiter=_delimiter).writerows(_data)

    return print(f"File {os.path.basename(_path)} is created")


def write_latest_commit(_config_file="config.ini", _sha1=""):
    config = ConfigParser()
    config.read(_config_file)
    config.set("reducer", "latest_reduced", _sha1)

    with open(_config_file, "w") as f:
        config.write(f)


def move_to_legacy(_path_master, _path_build, _path_legacy):
    if not os.path.exists(_path_master) and not os.path.exists(_path_build):
        exit(print("No master or build folder found"))

    if os.path.exists(_path_master):
        shutil.move(_path_master, _path_legacy)

        if os.path.exists(_path_build):
            shutil.rmtree(_path_build)

        return print("Master folder moved to legacy")

    if os.path.exists(_path_build):
        if os.path.exists(_path_legacy):
            shutil.rmtree(_path_legacy)

        shutil.move(_path_build, _path_legacy)

        return print("Build folder moved to legacy")

    if os.path.exists(_path_build):
        shutil.move(_path_build, _path_legacy)

        return print("Build folder moved to legacy")


def handle_modified(_modified, _sha1):
    if not _modified:
        return

    basename = [os.path.splitext(name)[0] for name in _modified]

    json_data = get_top_level_keys()

    removed = [i for i in json_data if i not in basename]

    for key in removed:
        write_to_child(key, "verifiedWith", _sha1)


def handle_deleted(_deleted, _path, _section):
    if not _deleted:
        return

    basename = [os.path.splitext(name)[0] for name in _deleted]

    for key in basename:
        print(f"Removing {key} from SMDB...")

        delete_key(key)

        os.remove(os.path.join(_path, f"{key}.txt"))

        move_to_legacy(
            os.path.join(_section["master"], key),
            os.path.join(_section["build"], key),
            os.path.join(_section["legacy"], key),
        )


def reducer():
    htgdb_sha1 = update_repo()
    section = load_config()

    if section["latest_reduced"] == htgdb_sha1:
        return print("Nothing new to reduce")

    path_smdb = os.path.join(os.getcwd(), section["orig_smdb"])
    path_reduced_smdb = os.path.join(os.getcwd(), section["new_smdb"])

    update_changes = git_difference(section["latest_reduced"], htgdb_sha1)

    input(json.dumps(update_changes, indent=4))

    if update_changes["renamed"]:
        input("Some files will be renamed, the program will end...")
        exit()

    if update_changes["added"]:
        input("Some files will be renamed, the program will end...")
        exit()

    handle_deleted(update_changes["deleted"], path_reduced_smdb, section)

    handle_modified(update_changes["modified"], htgdb_sha1)

    for database in update_changes["modified"] + update_changes["added"]:
        data = populate_list(os.path.join(path_smdb, database))
        basename = os.path.splitext(database)[0]

        new_file(os.path.join(path_reduced_smdb, database), "\t", single_file_db(data))
        write_to_child(basename, "extensions", get_extensions(data))

    write_latest_commit(_sha1=htgdb_sha1)


if __name__ == "__main__":
    reducer()
