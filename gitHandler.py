from git import GitCommandError, RemoteProgress, Repo
from tqdm import tqdm
import os


class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()

    def update(self, op_code, cur_count, max_count=None, message=""):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()


def update_repo(
    _repo_name="Hardware-Target-Game-Database",
    _url="https://github.com/frederic-mahe/Hardware-Target-Game-Database.git",
):
    if os.path.exists(_repo_name):
        print("Updating repo...")
        repo = Repo(_repo_name)
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

    Repo.clone_from(
        _url,
        to_path=_repo_name,
        progress=CloneProgress(),
    )

    return Repo(_repo_name).head.object.hexsha


def git_difference(
    _old_commit, _new_commit="HEAD", repo_name="Hardware-Target-Game-Database"
):
    repo = Repo(repo_name)

    old_commit = repo.commit(_old_commit)
    new_commit = repo.commit(_new_commit)

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
                "R": lambda: changes["renamed"].append(
                    {
                        "from": a_path,
                        "to": b_path,
                    }
                ),
            }[item.change_type]()

    return changes


def git_commit(_message, _add, _repo=os.getcwd()):
    if not _add:
        print("Nothing to commit")
        return

    repo = Repo(_repo)

    repo.git.add(*_add)

    repo.git.commit("-m", _message)

    origin = repo.remote(name="origin")
    origin.push()


def git_file_status(_path, _repo=os.getcwd()):
    repo = Repo(_repo)
    return repo.git.status("--porcelain", _path)
