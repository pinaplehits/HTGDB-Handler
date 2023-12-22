from compressHandler import uncompress
from configparser import ConfigParser
from datetime import datetime
from gitHandler import git_file_status, git_commit, git_push
from jsonHandler import get_top_level_keys, write_to_child, find_non_empty_key
from reducer import reducer
from smdbHandler import get_smdb_not_verified
import csv
import os
import shutil
import subprocess


def load_config(
    section: str = "build_reduced", file: str = "config.ini"
) -> tuple[dict, str]:
    config = ConfigParser()
    config.read(file)

    return dict(config.items(section)), config["reducer"]["latest_reduced"]


def select_database(sha1: str) -> tuple[list[str], list[str]]:
    json_keys = get_top_level_keys()
    missing = find_non_empty_key(json_keys, "missing")
    not_verified = get_smdb_not_verified(sha1, json_keys)

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


def all_smdb(json_keys: list[str]) -> tuple[list[str], list[str]]:
    os.system("clear" if os.name == "posix" else "cls")

    smdb = [f"{key}.txt" for key in json_keys]

    [print(index, value) for index, value in enumerate(json_keys)]
    index = input("Select one SMDB file: ")

    return [smdb[int(index)]], [json_keys[int(index)]]


def update_missing(missing: str, basename: str) -> None:
    if not os.path.exists(missing):
        write_to_child(basename, "missing", [])
        return

    with open(missing, "r") as f:
        missing_data = list(csv.reader(f, delimiter="\t"))
        write_to_child(basename, "missing", missing_data)

    os.remove(missing)


def build_from_masters(masters: str, basename: str, romimport: str) -> bool:
    name = os.path.basename(masters)

    if not os.path.exists(masters):
        print(f"Masters folder {name} doesn't exist")
        return False

    if not os.listdir(masters):
        print(f"Masters folder {name} is empty")
        return False

    masters = os.path.join(
        masters,
        f"{basename}.7z.001"
        if os.path.exists(os.path.join(masters, f"{basename}.7z.001"))
        else f"{basename}.7z",
    )

    uncompress(masters, romimport)

    return True


def build_from_main(folder: str, romimport: str) -> bool:
    name = os.path.basename(folder)

    if not os.path.exists(folder):
        print(f"Main folder {name} doesn't exist")
        return False

    if not os.listdir(folder):
        print(f"Main folder {name} is empty")
        return False

    if not os.path.exists(romimport):
        shutil.move(folder, romimport)
        return True

    for root, _, files in os.walk(folder):
        relative_path = os.path.relpath(root, folder)
        romimport_dir = os.path.join(romimport, relative_path)

        if not os.path.exists(romimport_dir):
            os.makedirs(romimport_dir)

        for file in files:
            folder_file = os.path.join(root, file)
            romimport_file = os.path.join(romimport_dir, file)
            if not os.path.exists(romimport_file):
                shutil.move(folder_file, romimport_file)

    shutil.rmtree(folder)

    return True


def build_from_verify(basename: str, smdb: str, mismatch: str) -> None:
    section, latest_reduced = load_config()

    romimport = os.path.join(section["romimport"], basename)
    folder = os.path.join(section["folder"], basename)
    missing = mismatch.replace("mismatch", "missing")

    if not build_from_main(folder, romimport):
        return

    run_script(
        section["script"], romimport, smdb, folder, missing, basename, latest_reduced
    )


def run_script(
    script: str,
    romimport: str,
    smdb: str,
    folder: str,
    missing: str,
    basename: str,
    latest_reduced: str,
) -> None:
    build = [
        "python",
        script,
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
        subprocess.check_call(build)
    except subprocess.CalledProcessError as e:
        print(f"Error executing the command: {e.returncode}")
        exit()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit()

    shutil.rmtree(romimport)

    update_missing(missing, basename)
    write_to_child(basename, "verifiedWith", latest_reduced)
    write_to_child(basename, "incorrectLocation", False)

    files = ["db.json"]
    date = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    git_message = f"Build updated {basename} in db.json on {date}"
    changes = [item for item in files if git_file_status(item)]

    print(git_message)
    git_commit(git_message, changes)
    git_push()


def build() -> None:
    section, latest_reduced = load_config()

    smdb, basename = select_database(latest_reduced)

    for smdb_file, basename_file in zip(smdb, basename):
        print(f"Building {basename_file}")
        missing = "missing_" + smdb_file
        romimport = os.path.join(section["romimport"], basename_file)

        folder = os.path.join(section["folder"], basename_file)
        smdb_file = os.path.join(section["smdb"], smdb_file)
        masters = os.path.join(section["masters"], basename_file)

        if not build_from_main(folder, romimport):
            if not build_from_masters(masters, basename_file, romimport):
                continue

        run_script(
            section["script"],
            romimport,
            smdb_file,
            folder,
            missing,
            basename_file,
            latest_reduced,
        )


if __name__ == "__main__":
    reducer()
    build()
