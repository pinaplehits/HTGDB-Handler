from configparser import ConfigParser
from git import Repo
import csv
import glob
import os
import re

# Configuration variables
fields = ["SHA256", "Path", "SHA1", "MD5", "CRC32", "Size"]


def populate_list(_path):
    with open(str(_path), newline="") as file:
        csv_reader = csv.reader(file, delimiter="\t")
        csv_list = list(csv_reader)
    return csv_list


def single_file_db(_data):
    dataset = set([item[0] for item in _data])

    if len(dataset) == len(_data):
        print("SMDB not reduced")
        return _data

    newdata = []

    for sublist_data in _data:
        if not dataset:
            break

        if sublist_data[0] in dataset:
            dataset.remove(sublist_data[0])
            newdata.append(sublist_data)

    print(f"SMDB reduced from {len(_data)} to {len(newdata)} files")

    return newdata


def new_file(_path, _delimiter, _data):
    with open(_path, "w", newline="") as file:
        csvwriter = csv.writer(file, delimiter=_delimiter)
        # csvwriter.writerow(fields)
        csvwriter.writerows(_data)


def get_extensions(items):
    file_extension = set()

    for item in items:
        split_text = os.path.splitext(os.path.basename(item[1]))
        file_extension.add(split_text[1].lower())

    print(sorted(file_extension))

    return sorted(file_extension)


def drop_first_folder(_path):
    _path = _path.split("/", 1)
    return _path[1]


def get_databases(_path=os.getcwd(), _files="*"):
    return [os.path.basename(x) for x in glob.glob(os.path.join(_path, _files))]


def git_head(_path=os.getcwd()):
    repo = Repo(path=_path, search_parent_directories=True)
    return repo.head.object.hexsha


def load_config(_config_file="config.ini"):
    config = ConfigParser()
    config.read(_config_file)

    return config["local"]["orig_smdb"], config["local"]["new_smdb"]


def re_files(_data, _regularexpresion):
    for index, value in enumerate(_data):
        _data[index] = re.split(_regularexpresion, value)
    return _data


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


def main():
    # Load config in file .ini
    og_smdb, reduced_smdb = load_config()

    # Set path for the workplace
    repos_path = os.path.dirname(os.path.normpath(os.getcwd()))
    path_smdb = os.path.normpath(os.path.join(repos_path, og_smdb))
    path_reduced_smdb = os.path.normpath(os.path.join(repos_path, reduced_smdb))

    # Get SMDB text files and the SHA-1 git head from the original repository
    databases = get_databases(path_smdb, "*.txt")
    htgdb_sha1 = git_head(path_smdb)

    # Check if the current directory is empty
    if os.listdir(path_reduced_smdb):
        items = re_files(get_databases(path_reduced_smdb, "*.txt"), "_|\.txt")
        sha1 = set([item[1] for item in items])

        # remove_files(items, split_text[0], htgdb_sha1, i)

    for database in databases:
        # for i in range(len(smdb_list)):
        split_text = os.path.splitext(database)
        filename = f"{split_text[0]}_{htgdb_sha1}.txt"

        if os.path.exists(filename):
            print(f"Filename {filename} already exists")
            continue

        smdb_location = os.path.join(path_smdb, database)
        data = populate_list(smdb_location)
        get_extensions(data)

        print(f"Creating {filename} file...")
        new_file(filename, "\t", single_file_db(data))
        print(
            f"File {filename} is created",
        )


main()
