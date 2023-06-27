from configparser import ConfigParser
import os
import subprocess
from smdbHandler import get_all_smdb


def load_config(_section="verify_reduced"):
    config_file = "config.ini"
    config = ConfigParser()
    config.read(config_file)

    return dict(config.items(_section))


def select_database(_path):
    smdb, basename = get_all_smdb(_path)

    [print(index, value) for index, value in enumerate(basename)]
    print(len(basename), "All")
    index = input("Select one SMDB file: ")

    if int(index) == len(basename):
        return smdb, basename

    return [smdb[int(index)]], [basename[int(index)]]


def verify():
    section = load_config()

    smdb, basename = select_database(section["smdb"])

    for smdb, basename in zip(smdb, basename):
        mismatch = os.path.join(section["mismatch"], f"{smdb}.txt")
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
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(e.output)


if __name__ == "__main__":
    verify()
