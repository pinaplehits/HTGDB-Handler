from venv import EnvBuilder
import os
import subprocess
import sys


def create_virtualenv(path: str) -> None:
    if os.path.isdir(path):
        return

    builder = EnvBuilder(with_pip=True, prompt=path)
    builder.create(path)


def activate_virtualenv(path: str) -> None:
    activate_script = "Scripts/activate" if sys.platform == "win32" else "bin/activate"
    activate_path = os.path.join(path, activate_script)


def install_package() -> None:
    # subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    )


if __name__ == "__main__":
    venv_path = ".venv"
    create_virtualenv(venv_path)

    install_package()
