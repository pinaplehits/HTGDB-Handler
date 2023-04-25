from configparser import ConfigParser
from git import Repo, GitCommandError
from gitHandler import CloneProgress
import csv
import os


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


def update_repo(_repo_name="Hardware-Target-Game-Database"):
    if os.path.exists(_repo_name):
        print("Updating repo...")
        repo = Repo(_repo_name)
        current_sha1 = repo.head.object.hexsha
        repo.git.checkout("master")
        repo.git.reset("--hard", repo.head.commit)

        try:
            repo.remotes.origin.pull(progress=CloneProgress())
        except GitCommandError as e:
            print("An error occurred while pulling changes: ", e)

        new_sha1 = repo.head.object.hexsha

        if current_sha1 == new_sha1:
            print("No new commits")
            return new_sha1

        print(f"Updated from {current_sha1} to {new_sha1}")
        return new_sha1

    Repo.clone_from(
        url="https://github.com/frederic-mahe/Hardware-Target-Game-Database.git",
        to_path=_repo_name,
        progress=CloneProgress(),
    )

    return Repo(_repo_name).head.object.hexsha


def write_latest_commit(_config_file="config.ini", _sha1=""):
    config = ConfigParser()
    config.read(_config_file)
    config.set("reducer", "latest_reduced", _sha1)

    with open(_config_file, "w") as f:
        config.write(f)


def remove_files(_path):
    for file in os.listdir(_path):
        os.remove(os.path.join(_path, file))


def reducer():
    htgdb_sha1 = update_repo()
    section = load_config()

    if section["latest_reduced"] == htgdb_sha1:
        return print("Nothing new to reduce")

    path_smdb = os.path.normpath(os.path.join(os.getcwd(), section["orig_smdb"]))
    path_reduced_smdb = os.path.normpath(os.path.join(os.getcwd(), section["new_smdb"]))

    remove_files(path_reduced_smdb)

    databases = [file for file in os.listdir(path_smdb) if file.endswith(".txt")]

    for database in databases:
        data = populate_list(os.path.join(path_smdb, database))
        print(get_extensions(data))

        new_file(os.path.join(path_reduced_smdb, database), "\t", single_file_db(data))

    write_latest_commit(_sha1=htgdb_sha1)


if __name__ == "__main__":
    reducer()
