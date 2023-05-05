from configparser import ConfigParser
import json
from jsonHandler import write_to_child, get_top_level_keys, read_from_child
from reducer import reducer
import csv
import os
import shutil


def load_config(_section="build_reduced", _file="config.ini"):
    config = ConfigParser()
    config.read(_file)

    return dict(config.items(_section)), config["reducer"]["latest_reduced"]


def select_database(_path, _sha1):
    smdb, basename = get_missing_smdb(_sha1)

    [print(index, value) for index, value in enumerate(basename)]
    print("999 for all SMDB files")
    index = input("Select one SMDB file: ")

    if index == "999":
        return get_all_smdb(_path)

    return smdb[int(index)], basename[int(index)]


def get_missing_smdb(_sha1):
    db = get_top_level_keys()
    missing = [x for x in db if read_from_child(x, "missing")]
    not_verified = [
        x
        for x in db
        if read_from_child(x, "verifiedWith") != _sha1
        or not read_from_child(x, "verifiedWith")
    ]

    basename = sorted(set(missing + not_verified))
    smdb = [f"{x}.txt" for x in basename]

    return smdb, basename


def get_all_smdb(_path):
    os.system("clear" if os.name == "posix" else "cls")

    smdb = sorted([x for x in os.listdir(_path) if x.endswith(".txt")], key=str.lower)
    basename = [os.path.splitext(os.path.basename(x))[0] for x in smdb]

    [print(index, value) for index, value in enumerate(basename)]
    index = input("Select one SMDB file: ")

    return smdb[int(index)], basename[int(index)]


def uncompress_7z(_file, _output_folder):
    os.system(f"7z x '{_file}' -o'{_output_folder}' -y")


def compress_7z(_basename, _path):
    os.system(f"7z a '{_basename}.7z' '{_path}/*' '-xr!{_path}'")


def update_missing(_missing, _basename):
    if not os.path.exists(_missing):
        write_to_child(_basename, "missing", [])
        return

    with open(_missing, "r") as f:
        missing_data = list(csv.reader(f, delimiter="\t"))
        write_to_child(_basename, "missing", missing_data)

    os.remove(_missing)


def build_from_masters(_masters, _basename, _romimport):
    if not os.path.exists(_masters):
        print(f"Masters folder {_masters} doesn't exist")
        return False

    if not os.listdir(_masters):
        print(f"Masters folder {_masters} is empty")
        return False

    _masters = os.path.join(
        _masters,
        f"{_basename}.7z.001"
        if os.path.exists(os.path.join(_masters, f"{_basename}.7z.001"))
        else f"{_basename}.7z",
    )

    uncompress_7z(_masters, _romimport)

    return True


def build_from_main(_folder, _romimport):
    if not os.path.exists(_folder):
        print(f"Main folder {_folder} doesn't exist")
        return False

    if not os.listdir(_folder):
        print(f"Main folder {_folder} is empty")
        return False

    shutil.move(_folder, _romimport)

    return True


def build():
    reducer()

    section, latest_reduced = load_config()

    smdb, basename = select_database(section["smdb"], latest_reduced)
    missing = os.path.join(section["missing"], smdb)
    romimport = os.path.join(section["romimport"], basename)

    folder = os.path.join(section["folder"], basename)
    smdb = os.path.join(section["smdb"], smdb)
    masters = os.path.join(section["masters"], basename)

    if not build_from_main(folder, romimport):
        if not build_from_masters(masters, basename, romimport):
            return print("No files to build")

    build = f"python {section['script']} --input_folder '{romimport}' --database '{smdb}' --output_folder '{folder}' --missing '{missing}' --skip_existing --drop_initial_directory --file_strategy hardlink"

    os.system(build)

    shutil.rmtree(romimport)

    update_missing(missing, basename)
    write_to_child(basename, "verifiedWith", latest_reduced)


if __name__ == "__main__":
    build()
