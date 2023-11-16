from configparser import ConfigParser
from jsonHandler import write_to_child
from smdbHandler import get_all_smdb
from build import build_from_verify
import os
import subprocess


def load_config(_section="verify_reduced", _file="config.ini"):
    config = ConfigParser()
    config.read(_file)

    return dict(config.items(_section))


def select_database(_path):
    smdb, basename = get_all_smdb(_path)

    [print(index, value) for index, value in enumerate(basename)]
    print(len(basename), "All")
    index = input("Select one SMDB file: ")

    if int(index) == len(basename):
        return smdb, basename

    return [smdb[int(index)]], [basename[int(index)]]


def handle_mismatch(_mismatch, _basename):
    if not os.path.exists(_mismatch):
        return

    categories = {
        "Incorrect Location Files:": [],
        "Extra Files:": [],
        "Missing Files:": [],
    }

    with open(_mismatch, "r") as file:
        current_category = None
        for line in file:
            line = line.strip()
            if line in categories:
                current_category = categories[line]
            elif current_category is not None and line:
                first_value = line.split("\t")[0]
                current_category.append(first_value)

    handle_incorrectLocations(categories["Incorrect Location Files:"], _basename)
    handle_extraFiles(categories["Extra Files:"])
    handle_missingFiles(categories["Missing Files:"], _basename)

    os.remove(_mismatch)

    if categories["Incorrect Location Files:"]:
        return True

    return False


def handle_incorrectLocations(_paths, _basename):
    if not _paths:
        return

    write_to_child(_basename, "incorrectLocation", True)


def handle_extraFiles(_paths):
    if not _paths:
        return

    print("Removing extra files...")

    for path in _paths:
        os.remove(path)


def handle_missingFiles(_paths, _basename):
    if not _paths:
        return

    write_to_child(_basename, "missing", _paths)


def verify():
    section = load_config()

    smdb, basename = select_database(section["smdb"])

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

        if not runBuildScript:
            write_to_child(
                basename, "verifiedWith", "9e32bb5abb8975231f2933ced6ff2e3d0b3c78ae"
            )

        if runBuildScript:
            build_from_verify(basename, smdb, mismatch)


if __name__ == "__main__":
    verify()
