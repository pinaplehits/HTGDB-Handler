from configparser import ConfigParser
from jsonHandler import write_to_child
from reducer import reducer
import csv
import os
import shutil


def load_config(_section="build_reduced", _file="config.ini"):
    config = ConfigParser()
    config.read(_file)

    return dict(config.items(_section)), config["reducer"]["latest_reduced"]


def select_database(_path):
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
        return False

    if not os.listdir(_masters):
        return False

    _masters = os.path.join(
        _masters,
        f"{_basename}.7z.001"
        if os.path.exists(os.path.join(_masters, f"{_basename}.7z.001"))
        else f"{_basename}.7z",
    )

    uncompress_7z(_masters, _romimport)

    return True


def build_from_uncompress(_romimport, _folder):
    if not os.path.exists(_folder):
        exit("No files to build")

    shutil.move(_folder, _romimport)


def build():
    reducer()

    section, latest_reduced = load_config()

    smdb, basename = select_database(section["smdb"])
    missing = os.path.join(section["missing"], smdb)
    romimport = os.path.join(section["romimport"], basename)

    folder = os.path.join(section["folder"], basename)
    smdb = os.path.join(section["smdb"], smdb)
    masters = os.path.join(section["masters"], basename)

    if not build_from_masters(masters, basename, romimport):
        build_from_uncompress()

    build = f"python {section['script']} --input_folder '{romimport}' --database '{smdb}' --output_folder '{folder}' --missing '{missing}' --skip_existing --drop_initial_directory --file_strategy hardlink"

    os.system(build)

    shutil.rmtree(romimport)

    update_missing(missing, basename)
    write_to_child(basename, "verifiedWith", latest_reduced)


if __name__ == "__main__":
    build()
