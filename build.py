from compressHandler import uncompress
from configparser import ConfigParser
from datetime import datetime
from gitHandler import git_file_status, git_commit
from jsonHandler import get_top_level_keys, write_to_child
from reducer import reducer
from smdbHandler import get_smdb_with_missing, get_smdb_not_verified
import csv
import os
import shutil
import subprocess


def load_config(_section="build_reduced", _file="config.ini"):
    config = ConfigParser()
    config.read(_file)

    return dict(config.items(_section)), config["reducer"]["latest_reduced"]


def select_database(_sha1):
    json_keys = get_top_level_keys()
    missing = get_smdb_with_missing(json_keys)
    not_verified = get_smdb_not_verified(_sha1, json_keys)

    basename = sorted(set(missing + not_verified))

    options = {
        index: (value, f"{value}.txt", value) for index, value in enumerate(basename)
    }

    options[len(basename)] = (missing, [f"{key}.txt" for key in missing], "All missing")
    options[len(basename) + 1] = (
        not_verified,
        [f"{key}.txt" for key in not_verified],
        "All not verified",
    )
    options[len(basename) + 2] = (
        basename,
        [f"{key}.txt" for key in basename],
        "All missing and not verified",
    )
    options[len(basename) + 3] = (
        json_keys,
        [f"{key}.txt" for key in json_keys],
        "All SMDB",
    )

    for index, value in options.items():
        print(index, value[2])

    print("999 All SMDB")
    index = input("Select one SMDB file: ")

    if int(index) in options:
        basename, smdb, _ = options[int(index)]

        if isinstance(basename, list):
            return smdb, basename

        return [smdb], [basename]

    if int(index) == 999:
        return all_smdb(json_keys)

    return [], []


def all_smdb(_json_keys):
    os.system("clear" if os.name == "posix" else "cls")

    smdb = [f"{key}.txt" for key in _json_keys]

    [print(index, value) for index, value in enumerate(_json_keys)]
    index = input("Select one SMDB file: ")

    return [smdb[int(index)]], [_json_keys[int(index)]]


def update_missing(_missing, _basename):
    if not os.path.exists(_missing):
        write_to_child(_basename, "missing", [])
        return

    with open(_missing, "r") as f:
        missing_data = list(csv.reader(f, delimiter="\t"))
        write_to_child(_basename, "missing", missing_data)

    os.remove(_missing)


def build_from_masters(_masters, _basename, _romimport):
    name = os.path.basename(_masters)

    if not os.path.exists(_masters):
        print(f"Masters folder {name} doesn't exist")
        return False

    if not os.listdir(_masters):
        print(f"Masters folder {name} is empty")
        return False

    _masters = os.path.join(
        _masters,
        f"{_basename}.7z.001"
        if os.path.exists(os.path.join(_masters, f"{_basename}.7z.001"))
        else f"{_basename}.7z",
    )

    uncompress(_masters, _romimport)

    return True


def build_from_main(_folder, _romimport):
    name = os.path.basename(_folder)

    if not os.path.exists(_folder):
        print(f"Main folder {name} doesn't exist")
        return False

    if not os.listdir(_folder):
        print(f"Main folder {name} is empty")
        return False

    if not os.path.exists(_romimport):
        shutil.move(_folder, _romimport)
        return True

    for root, _, files in os.walk(_folder):
        relative_path = os.path.relpath(root, _folder)
        romimport_dir = os.path.join(_romimport, relative_path)

        if not os.path.exists(romimport_dir):
            os.makedirs(romimport_dir)

        for file in files:
            folder_file = os.path.join(root, file)
            romimport_file = os.path.join(romimport_dir, file)
            if not os.path.exists(romimport_file):
                shutil.move(folder_file, romimport_file)

    shutil.rmtree(_folder)

    return True


def build_from_verify(_basename, _smdb, _mismatch):
    section, latest_reduced = load_config()

    romimport = os.path.join(section["romimport"], _basename)
    folder = os.path.join(section["folder"], _basename)
    missing = _mismatch.replace("mismatch", "missing")

    if not build_from_main(folder, romimport):
        return

    run_script(
        section["script"], romimport, _smdb, folder, missing, _basename, latest_reduced
    )


def run_script(
    _script, _romimport, _smdb, _folder, _missing, _basename, _latest_reduced
):
    build = [
        "python",
        _script,
        "--input_folder",
        _romimport,
        "--database",
        _smdb,
        "--output_folder",
        _folder,
        "--missing",
        _missing,
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

    shutil.rmtree(_romimport)

    update_missing(_missing, _basename)
    write_to_child(_basename, "verifiedWith", _latest_reduced)
    write_to_child(_basename, "incorrectLocation", False)

    files = ["db.json"]
    date = datetime.now().strftime("%d/%m/%y")
    git_message = f"Build updated {_basename} in db.json on {date}"
    changes = [item for item in files if git_file_status(item)]

    print(git_message)
    print(changes)
    git_commit(git_message, changes)


def build():
    section, latest_reduced = load_config()

    smdb, basename = select_database(latest_reduced)

    for smdb, basename in zip(smdb, basename):
        print(f"Building {basename}")
        missing = "missing_" + smdb
        romimport = os.path.join(section["romimport"], basename)

        folder = os.path.join(section["folder"], basename)
        smdb = os.path.join(section["smdb"], smdb)
        masters = os.path.join(section["masters"], basename)

        if not build_from_main(folder, romimport):
            if not build_from_masters(masters, basename, romimport):
                continue

        run_script(
            section["script"],
            romimport,
            smdb,
            folder,
            missing,
            basename,
            latest_reduced,
        )


if __name__ == "__main__":
    reducer()
    build()
