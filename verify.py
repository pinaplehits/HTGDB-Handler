from build import build_from_verify
from configparser import ConfigParser
from jsonHandler import write_to_child, get_top_level_keys
from reducer import reducer
import os
import subprocess


def load_config(section: str = "verify_reduced", file: str = "config.ini") -> dict:
    config = ConfigParser()
    config.read(file)

    return dict(config.items(section))


def select_database() -> tuple[list[str], list[str]]:
    basename = get_top_level_keys()
    smdb = [f"{key}.txt" for key in basename]

    [print(index, value) for index, value in enumerate(basename)]
    print(len(basename), "All")
    index = input("Select one SMDB file: ")

    if int(index) == len(basename):
        return smdb, basename

    return [smdb[int(index)]], [basename[int(index)]]


def handle_mismatch(mismatch: str, basename: str) -> bool:
    if not os.path.exists(mismatch):
        return False

    categories = {
        "Incorrect Location Files:": [],
        "Extra Files:": [],
        "Missing Files:": [],
    }

    with open(mismatch, "r") as file:
        current_category = None
        for line in file:
            line = line.strip()
            if line in categories:
                current_category = categories[line]
            elif current_category is not None and line:
                first_value = line.split("\t")[0]
                current_category.append(first_value)

    handle_incorrectLocations(categories["Incorrect Location Files:"], basename)
    handle_extraFiles(categories["Extra Files:"])
    handle_missingFiles(categories["Missing Files:"], basename)

    os.remove(mismatch)

    if categories["Incorrect Location Files:"]:
        return True

    return False


def handle_incorrectLocations(incorrect_locations: list[str], basename: str) -> None:
    if not incorrect_locations:
        return

    write_to_child(basename, "incorrectLocation", True)


def handle_extraFiles(extra_files: list[str]) -> None:
    if not extra_files:
        return

    print("Removing extra files...")

    for path in extra_files:
        os.remove(path)


def handle_missingFiles(missing_files: list[str], basename: str) -> None:
    if not missing_files:
        return

    write_to_child(basename, "missing", missing_files)


def verify() -> None:
    section = load_config()

    smdb, basename = select_database()

    for smdb, basename in zip(smdb, basename):
        mismatch = "mismatch_" + smdb
        smdb = os.path.join(section["smdb"], smdb)
        folder = os.path.join(section["folder"], basename)

        command = [
            "python",
            section["script"],
            "--folder",
            folder,
            "--database",
            smdb,
            "--mismatch",
            mismatch,
            "--drop_initial_directory",
        ]

        try:
            print("Verifying", basename)
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(e.output)

        runBuildScript = handle_mismatch(mismatch, basename)

        if runBuildScript:
            build_from_verify(basename, smdb, mismatch)


if __name__ == "__main__":
    reducer()
    verify()
