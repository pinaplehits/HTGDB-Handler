from configparser import ConfigParser
from git import Repo
from gitHandler import CloneProgress
import csv
import glob
import os
import re

# Configuration variables
fields = ["SHA256", "Path", "SHA1", "MD5", "CRC32", "Size"]


def load_config(_config_file="config.ini"):
    config = ConfigParser()
    config.read(_config_file)

    return config["local"]["orig_smdb"], config["local"]["new_smdb"]


def get_files(_path=os.getcwd(), _files="*"):
    return [os.path.basename(x) for x in glob.glob(os.path.join(_path, _files))]


def git_head(_path=os.getcwd()):
    return Repo(path=_path, search_parent_directories=True).head.object.hexsha


def populate_list(_path):
    with open(str(_path), newline="") as file:
        csv_reader = csv.reader(file, delimiter="\t")
        return list(csv_reader)


def get_extensions(items):
    return sorted(
        set([os.path.splitext(os.path.basename(item[1]))[1].lower() for item in items])
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
    with open(_path, "w", newline="") as file:
        csvwriter = csv.writer(file, delimiter=_delimiter)
        # csvwriter.writerow(fields)
        csvwriter.writerows(_data)


def re_files(_data, _regex):
    return [re.split(_regex, value) for value in _data]


def update_repo():
    if os.path.exists("Hardware-Target-Game-Database"):
        print("Updating repo...")
        repo = Repo("Hardware-Target-Game-Database")
        repo.git.checkout("master")
        repo.git.reset("--hard", repo.head.commit)
        repo.remotes.origin.pull(progress=CloneProgress())
        print("Repo updated")
        return

    Repo.clone_from(
        url="https://github.com/frederic-mahe/Hardware-Target-Game-Database.git",
        to_path=os.path.join(os.getcwd(), "Hardware-Target-Game-Database"),
        progress=CloneProgress(),
    )


def main():
    update_repo()
    # Load config in file .ini
    og_smdb, reduced_smdb = load_config()

    # Set path for the workplace
    path_smdb = os.path.normpath(os.path.join(os.getcwd(), og_smdb))
    path_reduced_smdb = os.path.normpath(os.path.join(os.getcwd(), reduced_smdb))

    # Get SMDB text files and the SHA-1 git head from the original repository
    databases = get_files(path_smdb, "*.txt")
    htgdb_sha1 = git_head(path_smdb)

    for database in databases:
        split_text = os.path.splitext(database)
        file = f"{split_text[0]}_{htgdb_sha1}.txt"

        if os.path.exists(os.path.join(path_reduced_smdb, file)):
            print(f"File {file} already exists")
            continue

        data = populate_list(os.path.join(path_smdb, database))
        print(get_extensions(data))

        print(f"Creating {file} file...")
        new_file(os.path.join(path_reduced_smdb, file), "\t", single_file_db(data))
        print(f"File {file} is created")


main()
