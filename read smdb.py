from configparser import ConfigParser
from git import Repo
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


# def remove_files(_data, _filename, _sha1, i):
#     filename = f"{_data[i][0]}_{_data[i][1]}.txt"

#     for sublist_data in _data:
#         if sublist_data[0] == _filename:
#             if sublist_data[1] != _sha1:
#                 os.remove(filename)
#                 print(f"File {filename} removed")
#                 return
#             if sublist_data[1] == _sha1:
#                 return

#     # delete file if contains a string


def main():
    # Load config in file .ini
    og_smdb, reduced_smdb = load_config()

    # Set path for the workplace
    repos_path = os.path.dirname(os.path.normpath(os.getcwd()))
    path_smdb = os.path.normpath(os.path.join(repos_path, og_smdb))
    path_reduced_smdb = os.path.normpath(os.path.join(repos_path, reduced_smdb))

    # Get SMDB text files and the SHA-1 git head from the original repository
    databases = get_files(path_smdb, "*.txt")
    htgdb_sha1 = git_head(path_smdb)

    # # Check if the current directory is empty
    # if os.listdir(path_reduced_smdb):
    #     items = re_files(get_files(path_reduced_smdb, "*.txt"), "_|\.txt")
    #     sha1 = set([item[1] for item in items])

    #     #  remove_files(items, split_text[0], htgdb_sha1, i)

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
