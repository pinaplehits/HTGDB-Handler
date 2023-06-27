import subprocess
import sys


def install_package():
    packages = ["GitPython", "tqdm", "python-dotenv", "paramiko"]

    for package in packages:
        result = subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package]
        )

        if result != 0:
            print(f"Error installing {package}")
            exit()


install_package()
