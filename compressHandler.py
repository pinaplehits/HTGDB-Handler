import os
import subprocess


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


def compress_7z(_basename, _path):
    os.system(f"7z a '{_basename}.7z' '{_path}/*' '-xr!{_path}'")
