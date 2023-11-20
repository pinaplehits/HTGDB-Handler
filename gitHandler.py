from dotenv import load_dotenv
from git import GitCommandError, RemoteProgress, Repo
from tqdm import tqdm
import os
from typing import Dict, List, Union


class CloneProgress(RemoteProgress):
    def __init__(self) -> None:
        super().__init__()
        self.pbar = tqdm()

    def update(
        self,
        op_code: int,
        cur_count: int,
        max_count: Union[int, None],
        message: str = "",
    ) -> None:
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()


def update_repo(
    repo_name: str = "Hardware-Target-Game-Database",
    url: str = "https://github.com/frederic-mahe/Hardware-Target-Game-Database.git",
) -> str:
    if os.path.exists(repo_name):
        print("Updating repo...")
        repo = Repo(repo_name)
        current_sha1 = repo.head.object.hexsha
        repo.git.checkout("master")
        repo.git.reset("--hard", repo.head.commit)

        try:
            repo.remotes.origin.pull(progress=CloneProgress())
        except GitCommandError as e:
            print("An error occurred while pulling changes: ", e)

        new_sha1 = repo.head.object.hexsha

        if current_sha1 == new_sha1:
            print("No new commits")
            return new_sha1

        print(f"Updated from {current_sha1} to {new_sha1}")
        return new_sha1

    Repo.clone_from(url, to_path=repo_name, progress=CloneProgress())

    return Repo(repo_name).head.object.hexsha


def git_difference(
    old_commit: str,
    new_commit: str = "HEAD",
    repo_name: str = "Hardware-Target-Game-Database",
) -> Dict[str, List[Union[str, Dict[str, str]]]]:
    repo = Repo(repo_name)

    old_commit = repo.commit(old_commit)
    new_commit = repo.commit(new_commit)

    index = old_commit.diff(new_commit)

    changes = {"added": [], "deleted": [], "modified": [], "renamed": []}

    for item in index:
        if item.b_path.startswith("EverDrive Pack SMDBs") and item.b_path.endswith(
            ".txt"
        ):
            if item.a_blob is not None:
                a_path = os.path.basename(item.a_blob.path)

            if item.b_blob is not None:
                b_path = os.path.basename(item.b_blob.path)

            {
                "D": lambda: changes["deleted"].append(a_path),
                "M": lambda: changes["modified"].append(b_path),
                "A": lambda: changes["added"].append(b_path),
                "R": lambda: changes["renamed"].append({"from": a_path, "to": b_path}),
            }[item.change_type]()

    return changes


def set_git_config(repo: Repo) -> None:
    username = input("Enter your Git username: ")
    email = input("Enter your Git email: ")

    repo.config_writer().set_value("user", "name", username).release()
    repo.config_writer().set_value("user", "email", email).release()


def create_env_file() -> None:
    username = input("Enter the Github username: ")
    access_token = input("Enter the Github access token: ")

    with open(".env", "w") as f:
        f.write(f"GITHUB_USERNAME={username}\n")
        f.write(f"GITHUB_ACCESS_TOKEN={access_token}\n")


def git_commit(message: str, add: List[str], repo: str = os.getcwd()) -> None:
    if not add:
        print("Nothing to commit")
        return

    repo = Repo(repo)

    repo.git.add(*add)

    try:
        repo.git.commit("-m", message)
    except GitCommandError as e:
        if "Author identity unknown" in str(e):
            set_git_config(repo)
            repo.git.commit("-m", message)
        else:
            print("An error occurred while committing changes: ", e)
            exit()


def git_push(repo: str = os.getcwd()) -> None:
    repo = Repo(repo)

    if not load_dotenv():
        create_env_file()

    load_dotenv()
    username = os.environ.get("GITHUB_USERNAME")
    access_token = os.environ.get("GITHUB_ACCESS_TOKEN")

    remote_url = (
        f"https://{username}:{access_token}@github.com/pinaplehits/HTGDB-Handler.git"
    )

    origin = repo.remote(name="origin")
    origin.set_url(remote_url)
    print("Pushing changes...")
    origin.push()


def git_file_status(path: str, repo: str = os.getcwd()) -> str:
    repo = Repo(repo)
    return repo.git.status("--porcelain", path)
