from configparser import ConfigParser
import os


def load_config(_section="verify_reduced"):
    config_file = "config.ini"
    config = ConfigParser()
    config.read(config_file)

    return dict(config.items(_section))


def select_database(_path):
    files = [x for x in os.listdir(_path) if x.endswith(".txt")]
    files.sort(key=str.lower)

    basename = [filename.split("_")[0] for filename in files]

    [print(index, value) for index, value in enumerate(basename)]

    index = input("Select one SMDB file: ")

    return files[int(index)], basename[int(index)]


def main():
    section = load_config()

    smdb, folder = select_database(section["smdb"])
    smdb = os.path.join(section["smdb"], smdb)
    folder = os.path.join(section["folder"], folder)

    # print("Running script: " + section["script"])
    # print("Folder: " + section["folder"])
    # print("SMDB: " + section["smdb"])
    # print("Mismatch: " + section["mismatch"])

    command = f"python {section['script']} --folder '{section['folder']}' --database '{smdb}' --mismatch '{section['mismatch']}' --drop_initial_directory"
    input(command)
    os.system(command)


main()
