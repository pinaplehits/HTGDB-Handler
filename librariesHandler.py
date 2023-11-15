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


def install_package():
    # subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    )


if __name__ == "__main__":
    venv_path = ".venv"
    create_virtualenv(venv_path)

    install_package()
