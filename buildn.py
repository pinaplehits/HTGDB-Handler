from configparser import ConfigParser
import os
import shutil


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


def uncompress_7z(_file, _output_folder):
    os.system(f"7z x '{_file}' -o'{_output_folder}' -y")


def compress_7z(_basename, _path):
    os.system(f"7z a '{_basename}.7z' '{_path}/*' '-xr!{_path}'")


def updateDB(_missing):
    if os.path.exists(_missing):
        print("Missing file found")
        exit()

    print("Updating DB")


def main():
    section = load_config()

    smdb, basename = select_database(section["smdb"])
    missing = os.path.join(section["missing"], f"{basename}.txt")
    romimport = os.path.join(section["romimport"], basename)

    folder = os.path.join(section["folder"], basename)
    smdb = os.path.join(section["smdb"], smdb)
    masters = os.path.join(section["masters"], basename)

    if os.path.exists(masters):
        masters = os.path.join(
            masters,
            f"{basename}.7z.001" if len(os.listdir(masters)) > 1 else f"{basename}.7z",
        )

        uncompress_7z(masters, romimport)
    else:
        print("No latest folder found")
        exit()

    build = f"python {section['script']} --input_folder '{romimport}' --database '{smdb}' --output_folder '{folder}' --missing '{missing}' --skip_existing --drop_initial_directory --file_strategy hardlink"

    os.system(build)

    shutil.rmtree(romimport)

    updateDB(missing)


main()
