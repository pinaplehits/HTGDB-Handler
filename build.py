from configparser import ConfigParser
import csv
import json
import os
from reducer import reducer
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


def write_to_child(_basename, _child, _data, _json_db="db.json"):
    json_data = {}

    try:
        with open(_json_db, "r") as f:
            json_data = json.load(f)
    except json.decoder.JSONDecodeError:
        pass

    if _basename not in json_data:
        json_data[_basename] = {}

    json_data[_basename][_child] = _data

    with open(_json_db, "w") as f:
        json.dump(json_data, f, indent=2, sort_keys=True)


def build():
    # reducer()

    section, latest_reduced = load_config()

    smdb, basename = select_database(section["smdb"])
    missing = os.path.join(section["missing"], smdb)
    romimport = os.path.join(section["romimport"], basename)

    folder = os.path.join(section["folder"], basename)
    smdb = os.path.join(section["smdb"], smdb)
    masters = os.path.join(section["masters"], basename)

    if os.path.exists(masters):
        masters = os.path.join(
            masters,
            f"{basename}.7z.001"
            if os.path.exists(os.path.join(masters, f"{basename}.7z.001"))
            else f"{basename}.7z",
        )

        uncompress_7z(masters, romimport)
    else:
        if not os.path.exists(folder):
            return print(f"{os.path.basename(folder)} not found")

        shutil.move(folder, romimport)

    build = f"python {section['script']} --input_folder '{romimport}' --database '{smdb}' --output_folder '{folder}' --missing '{missing}' --skip_existing --drop_initial_directory --file_strategy hardlink"

    os.system(build)

    shutil.rmtree(romimport)

    update_missing(missing, basename)
    write_to_child(basename, "verifiedWith", latest_reduced)


if __name__ == "__main__":
    build()
