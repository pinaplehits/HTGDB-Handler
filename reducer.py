from configparser import ConfigParser
from gitHandler import update_repo, git_difference, git_commit, git_file_status
from jsonHandler import (
    get_top_level_keys,
    delete_key,
    write_to_child,
    sort_json,
    write_to_key,
)
from smdbHandler import get_extensions, read_file
import csv
import os
import shutil


def load_config(_section="reducer", _file="config.ini"):
    config = ConfigParser()
    config.read(_file)

    return dict(config.items(_section))


def reduce_db(_items):
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


def new_file(_path, _data, _delimiter="\t"):
    print(f"Creating {os.path.basename(_path)} file...")

    with open(_path, "w", newline="") as f:
        csv.writer(f, delimiter=_delimiter).writerows(_data)

    print(f"File {os.path.basename(_path)} is created")


def write_latest_commit(_config_file="config.ini", _sha1=""):
    config = ConfigParser()
    config.read(_config_file)
    config.set("reducer", "latest_reduced", _sha1)

    with open(_config_file, "w") as f:
        config.write(f)


def move_to_legacy(path_master, path_build, path_legacy):
    if not os.path.exists(path_master) and not os.path.exists(path_build):
        print("No master or build folder found")
        return

    print("Moving folders to legacy...")

    if os.path.exists(path_legacy):
        shutil.rmtree(path_legacy)

    if os.path.exists(path_master) and os.listdir(path_master):
        shutil.move(path_master, path_legacy)
        print("Master folder moved to legacy")
    elif os.path.exists(path_build) and os.listdir(path_build):
        shutil.move(path_build, path_legacy)
        print("Build folder moved to legacy")

    if os.path.exists(path_build):
        shutil.rmtree(path_build)


def handle_modified(_modified, _sha1, _added):
    if not _modified:
        print("No modified files found")
        return

    basename = set([os.path.splitext(name)[0] for name in _modified + _added])

    json_data = get_top_level_keys()

    removed = [i for i in json_data if i not in basename]

    print("Updating verifiedWith in db.json..")
    for key in removed:
        write_to_child(key, "verifiedWith", _sha1)


def handle_deleted(_deleted, _path, _section):
    if not _deleted:
        print("No deleted files found")
        return

    basename = [os.path.splitext(name)[0] for name in _deleted]

    print("Removing deleted from SMDB...")
    for key in basename:
        delete_key(key)

        os.remove(os.path.join(_path, f"{key}.txt"))

        move_to_legacy(
            os.path.join(_section["master"], key),
            os.path.join(_section["build"], key),
            os.path.join(_section["legacy"], key),
        )


def handle_renamed(_renamed):
    if not _renamed:
        print("No renamed files found")
        return

    input("Some files will be renamed, the program will end...")
    exit()


def handle_added(_added, _build_path, _master_path):
    if not _added:
        print("No added files found")
        return
    basename = [os.path.splitext(name)[0] for name in _added]

    print("Creating new folders...")
    [
        (os.makedirs(os.path.join(path, item), exist_ok=True), write_to_key(item))
        for path in [_build_path, _master_path]
        for item in basename
    ]


def check_file_changes(_changes, _path_smdb, _additional_files=[]):
    changes = [
        _path_smdb + value
        for value_list in _changes.values()
        for value in value_list
        if value
    ]

    changes.extend(_additional_files)

    return [item for item in changes if git_file_status(item)]


def reducer():
    htgdb_sha1 = update_repo()
    section = load_config()

    if section["latest_reduced"] == htgdb_sha1:
        return print("Nothing new to reduce")

    path_smdb = os.path.join(os.getcwd(), section["orig_smdb"])
    path_reduced_smdb = os.path.join(os.getcwd(), section["new_smdb"])

    update_changes = git_difference(section["latest_reduced"], htgdb_sha1)

    handle_renamed(update_changes.get("renamed"))

    handle_added(update_changes.get("added"), section["build"], section["master"])

    handle_deleted(update_changes.get("deleted"), path_reduced_smdb, section)

    handle_modified(
        update_changes.get("modified"), htgdb_sha1, update_changes.get("added")
    )

    for database in update_changes.get("added") + update_changes.get("modified"):
        data = read_file(os.path.join(path_smdb, database))
        basename = os.path.splitext(database)[0]
        newdb = reduce_db(data)

        new_file(os.path.join(path_reduced_smdb, database), newdb)
        write_to_child(basename, "extensions", get_extensions(newdb))
        write_to_child(basename, "reducedTo", len(newdb))
        write_to_child(basename, "reducedFrom", len(data))

    sort_json()
    write_latest_commit(_sha1=htgdb_sha1)

    git_message = f"Reduced from {section['latest_reduced']} to {htgdb_sha1}"

    changes = check_file_changes(
        update_changes, section["new_smdb"], ["db.json", "config.ini"]
    )

    git_commit(git_message, changes)


if __name__ == "__main__":
    reducer()
