from git import RemoteProgress, Repo
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


def gitDifference(
    _old_commit, _new_commit="HEAD", repo_name="Hardware-Target-Game-Database"
):
    repo = Repo(repo_name)

    old_commit = repo.commit(_old_commit)
    new_commit = repo.commit(_new_commit)

    index = old_commit.diff(new_commit)

    changes = {"add": [], "delete": [], "modified": [], "renamed": []}

    for item in index:
        if item.b_path.startswith("EverDrive Pack SMDBs") and item.b_path.endswith(
            ".txt"
        ):
            if item.a_blob is not None:
                a_path = os.path.basename(item.a_blob.path)

            if item.b_blob is not None:
                b_path = os.path.basename(item.b_blob.path)

            {
                "D": lambda: changes["delete"].append(a_path),
                "M": lambda: changes["modified"].append(b_path),
                "A": lambda: changes["add"].append(b_path),
                "R": lambda: changes["renamed"].append(
                    {
                        "from": a_path,
                        "to": b_path,
                    }
                ),
            }[item.change_type]()

    return changes
