from configparser import ConfigParser
import os


def load_config(_section="build_reduced"):
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


# Create a function to uncompress the 7z file in a specific folder
def uncompress_7z(_file, _folder):
    command = f"7z x -y -o{_folder} {_file}"
    input(command)
    os.system(command)


def main():
    section = load_config()

    smdb, basename = select_database(section["smdb"])
    missing = os.path.join(section["missing"], f"missing_{smdb}.txt")
    romimport = os.path.join(section["romimport"], basename)

    folder = os.path.join(section["folder"], basename)
    latest = os.path.join(folder, "latest", f"{basename}.7z")

    print(latest)
    print(folder)
    smdb = os.path.join(section["smdb"], smdb)

    # Uncompress the 7z file in the latest folder
    uncompress_7z(latest, romimport)

    command = f"python {section['script']} --input_folder '{romimport}' --database '{smdb}' --output_folder '{folder}' --missing '{missing}' --skip_existing --drop_initial_directory --file_strategy hardlink"

    os.system(command)


main()
