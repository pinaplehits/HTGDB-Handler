from configparser import ConfigParser
from datetime import datetime
from gitHandler import git_file_status, git_commit
from jsonHandler import write_to_child, get_top_level_keys, read_from_child, sort_json
from reducer import reducer
from smdbHandler import get_all_smdb
import csv
import os
import shutil
import subprocess


def load_config(_section="build_reduced", _file="config.ini"):
    config = ConfigParser()
    config.read(_file)

    return dict(config.items(_section)), config["reducer"]["latest_reduced"]


def select_database(_path, _sha1):
    smdb, basename = missing_smdb(_sha1)

    [print(index, value) for index, value in enumerate(basename)]
    print("999 for all SMDB files")
    index = input("Select one SMDB file: ")

    if index == "999":
        return all_smdb(_path)

    return smdb[int(index)], basename[int(index)]


def missing_smdb(_sha1):
    db = get_top_level_keys()
    missing = [x for x in db if read_from_child(x, "missing")]
    not_verified = [
        x
        for x in db
        if (verified := read_from_child(x, "verifiedWith")) != _sha1 or not verified
    ]

    basename = sorted(set(missing + not_verified))
    smdb = [f"{x}.txt" for x in basename]

    return smdb, basename


def all_smdb(_path):
    os.system("clear" if os.name == "posix" else "cls")

    smdb, basename = get_all_smdb(_path)

    [print(index, value) for index, value in enumerate(basename)]
    index = input("Select one SMDB file: ")

    return smdb[int(index)], basename[int(index)]


def uncompress_7z(_file, _output_folder):
    uncompress = [
        "7z",
        "x",
        _file,
        f"-o{_output_folder}",
        "-y",
        "-aoa",
    ]

    try:
        subprocess.run(uncompress, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e.returncode}")
        exit()
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        exit()


def compress_7z(_basename, _path):
    os.system(f"7z a '{_basename}.7z' '{_path}/*' '-xr!{_path}'")


def update_missing(_missing_path, _basename):
    if not os.path.exists(_missing_path):
        write_to_child(_basename, "missing", [])
        return

    with open(_missing_path, "r") as f:
        missing_data = list(csv.reader(f, delimiter="\t"))
        write_to_child(_basename, "missing", missing_data)

    os.remove(_missing_path)


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

    if not os.path.exists(_romimport):
        shutil.move(_folder, _romimport)
        return True

    for root, _, files in os.walk(_folder):
        relative_path = os.path.relpath(root, _folder)
        romimport_dir = os.path.join(_romimport, relative_path)

        if not os.path.exists(romimport_dir):
            input(f"romimport_dir: {romimport_dir}")
            os.makedirs(romimport_dir)

        for file in files:
            folder_file = os.path.join(root, file)
            romimport_file = os.path.join(romimport_dir, file)
            if not os.path.exists(romimport_file):
                shutil.move(folder_file, romimport_file)

    shutil.rmtree(_folder)

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

    build = [
        "python",
        section["script"],
        "--input_folder",
        romimport,
        "--database",
        smdb,
        "--output_folder",
        folder,
        "--missing",
        missing,
        "--skip_existing",
        "--drop_initial_directory",
        "--file_strategy",
        "hardlink",
    ]

    try:
        subprocess.run(build, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e.returncode}")
        exit()
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        exit()

    shutil.rmtree(romimport)

    update_missing(missing, basename)
    write_to_child(basename, "verifiedWith", latest_reduced)
    sort_json()

    files = ["db.json"]
    date = datetime.now().strftime("%d/%m/%y")
    git_message = f"Build updated {basename} in db.json on {date}"
    changes = [item for item in files if git_file_status(item)]

    git_commit(git_message, changes)


if __name__ == "__main__":
    build()
