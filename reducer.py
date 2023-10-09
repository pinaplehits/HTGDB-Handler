from configparser import ConfigParser
from gitHandler import update_repo, git_difference, git_commit, git_file_status
from jsonHandler import (
    get_top_level_keys,
    delete_key,
    write_to_child,
    write_to_key,
)
from smdbHandler import get_extensions, read_file, create_new_file
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


def write_latest_commit(_sha1, _file="config.ini"):
    if not _sha1:
        print("No SHA1 found")
        return

    config = ConfigParser()
    config.read(_file)
    config.set("reducer", "latest_reduced", _sha1)

    with open(_file, "w") as f:
        config.write(f)


def move_folder_to_legacy(_path_master, _path_build, _path_legacy):
    if not os.path.exists(_path_master) and not os.path.exists(_path_build):
        print("No master or build folder found")
        return

    print("Moving folders to legacy...")

    if os.path.exists(_path_legacy):
        shutil.rmtree(_path_legacy)

    if os.path.exists(_path_master) and os.listdir(_path_master):
        shutil.move(_path_master, _path_legacy)
        print("Master folder moved to legacy")
    elif os.path.exists(_path_build) and os.listdir(_path_build):
        shutil.move(_path_build, _path_legacy)
        print("Build folder moved to legacy")

    if os.path.exists(_path_build):
        shutil.rmtree(_path_build)


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

        move_folder_to_legacy(
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


def check_git_changes(_git_changes, _path, _extra_files=[]):
    changes = [
        _path + value for values in _git_changes.values() for value in values if value
    ]

    changes.extend(_extra_files)

    return [item for item in changes if git_file_status(item)]


def reducer():
    htgdb_sha1 = update_repo()
    section = load_config()

    if section["latest_reduced"] == htgdb_sha1:
        return print("Nothing new to reduce")

    path_smdb = os.path.join(os.getcwd(), section["orig_smdb"])
    path_reduced_smdb = os.path.join(os.getcwd(), section["new_smdb"])

    git_changes = git_difference(section["latest_reduced"], htgdb_sha1)

    handle_renamed(git_changes.get("renamed"))

    handle_added(git_changes.get("added"), section["build"], section["master"])

    handle_deleted(git_changes.get("deleted"), path_reduced_smdb, section)

    handle_modified(git_changes.get("modified"), htgdb_sha1, git_changes.get("added"))

    for database in git_changes.get("added") + git_changes.get("modified"):
        data = read_file(os.path.join(path_smdb, database))
        basename = os.path.splitext(database)[0]
        newdb = reduce_db(data)

        create_new_file(os.path.join(path_reduced_smdb, database), newdb)
        write_to_child(basename, "extensions", get_extensions(newdb))
        write_to_child(basename, "reducedTo", len(newdb))
        write_to_child(basename, "reducedFrom", len(data))
        write_to_child(basename, "compressed", False)

    write_latest_commit(htgdb_sha1)

    git_message = f"Reduced from {section['latest_reduced']} to {htgdb_sha1}"
    extra_files = ["db.json", "config.ini"]
    changes = check_git_changes(git_changes, section["new_smdb"], extra_files)

    git_commit(git_message, changes)


if __name__ == "__main__":
    reducer()
