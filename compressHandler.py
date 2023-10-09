import os
import shutil
import subprocess
from jsonHandler import write_to_child


def uncompress(_file, _output_folder):
    uncompress = [
        "7z",
        "x",
        _file,
        f"-o{_output_folder}",
        "-y",
        "-aoa",
    ]

    try:
        subprocess.run(uncompress, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e.returncode}")
        exit()
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        exit()


def compress(_basename, _input_path, _output_path):
    output_path = os.path.join(_output_path, f"{_basename}.7z")

    if not _input_path.endswith("/"):
        _input_path += "/"

    compress = [
        "7z",
        "-mx=9",
        "-mmt=4",
        "-v2g",
        "a",
        output_path,
        _input_path,
    ]

    if not os.path.exists(_output_path):
        os.makedirs(_output_path)

    if os.listdir(_output_path):
        shutil.rmtree(_output_path)
        os.makedirs(_output_path)

    try:
        subprocess.run(compress, check=True)
        write_to_child(_basename, "compressed", True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e.returncode}")
        exit()
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        exit()


if __name__ == "__main__":
    compress(
        "test",
        "Reduced SMDBs/",
        "test with spaces/test/",
    )
