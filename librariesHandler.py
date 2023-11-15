from venv import EnvBuilder
import os
import subprocess
import sys


def create_virtualenv(_path):
    if os.path.isdir(_path):
        return

    builder = EnvBuilder(with_pip=True, prompt=_path)
    builder.create(_path)


def activate_virtualenv(_path):
    activate_script = "Scripts/activate" if sys.platform == "win32" else "bin/activate"
    activate_path = os.path.join(_path, activate_script)


def install_packages():
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)


def install_package():
    dirname = ".venv"
    create_virtualenv(dirname)

    activate_virtualenv(dirname)

    install_packages()


if __name__ == "__main__":
    install_package()
