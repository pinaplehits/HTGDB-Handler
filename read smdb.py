from configparser import ConfigParser
from git import Repo, GitCommandError
from gitHandler import CloneProgress
import csv
import os

# Configuration variables
fields = ["SHA256", "Path", "SHA1", "MD5", "CRC32", "Size"]


def load_config(_config_file="config.ini"):
    config = ConfigParser()
    config.read(_config_file)

    return config["local"]["orig_smdb"], config["local"]["new_smdb"]


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


def update_repo():
    if os.path.exists("Hardware-Target-Game-Database"):
        print("Updating repo...")
        repo = Repo("Hardware-Target-Game-Database")
        current_sha1 = repo.head.object.hexsha
        repo.git.checkout("master")
        repo.git.reset("--hard", repo.head.commit)

        try:
            repo.remotes.origin.pull(progress=CloneProgress())
        except GitCommandError as e:
            print("An error occurred while pulling changes: ", e)

        new_sha1 = repo.head.object.hexsha

        if current_sha1 == new_sha1:
            exit(print("No new commits"))

        print(f"Updated from {current_sha1} to {new_sha1}")

        return new_sha1

    Repo.clone_from(
        url="https://github.com/frederic-mahe/Hardware-Target-Game-Database.git",
        to_path=os.path.join(os.getcwd(), "Hardware-Target-Game-Database"),
        progress=CloneProgress(),
    )


def main():
    htgdb_sha1 = update_repo()
    # Load config in file .ini
    og_smdb, reduced_smdb = load_config()

    # Set path for the workplace
    path_smdb = os.path.normpath(os.path.join(os.getcwd(), og_smdb))
    path_reduced_smdb = os.path.normpath(os.path.join(os.getcwd(), reduced_smdb))

    # Get SMDB text files and the SHA-1 git head from the original repository
    databases = [file for file in os.listdir(path_smdb) if file.endswith(".txt")]

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
