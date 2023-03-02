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


def drop_first_folder(_path):
    _path = _path.split("/", 1)
    return _path[1]


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
    databases = get_files(path_smdb, "*.txt")
    htgdb_sha1 = git_head(path_smdb)

    # # Check if the current directory is empty
    # if os.listdir(path_reduced_smdb):
    #     items = re_files(get_databases(path_reduced_smdb, "*.txt"), "_|\.txt")
    #     sha1 = set([item[1] for item in items])

    #      remove_files(items, split_text[0], htgdb_sha1, i)

    for database in databases:
        split_text = os.path.splitext(database)
        file = f"{split_text[0]}_{htgdb_sha1}.txt"

        # if os.path.exists(os.path.join(path_reduced_smdb, file)):
        #     print(f"File {file} already exists")
        #     continue

        data = populate_list(os.path.join(path_smdb, database))
        print(get_extensions(data))

        print(f"Creating {file} file...")
        new_file(file, "\t", single_file_db(data))
        print(f"File {file} is created")


main()
