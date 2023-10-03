import hashlib
import json
import os


def hash_files(directory=os.getcwd()):
    files = get_files_recursively(directory)
    file_dict = {}
    for file in files:
        with open(file, "rb") as f:
            try:
                file_dict[file] = hashlib.sha256(f.read()).hexdigest()
            except IOError:
                print(f"Error al leer el archivo {file}")
    return file_dict


def create_json(file_dict, filename="file_hash.json"):
    with open(filename, "w") as f:
        json.dump(file_dict, f, indent=2, sort_keys=True)


def get_files_recursively(directory=os.getcwd()):
    list_files = []

    if not os.path.isdir(directory):
        raise ValueError(f"La ruta {directory} no es un directorio válido")

    for root, _, files in os.walk(directory):
        for file in files:
            if file == "file_hash.json" or file == "SHA256.py":
                continue

            path = os.path.join(root, file)
            list_files.append(path)

    return list_files


if __name__ == "__main__":
    create_json(hash_files())
