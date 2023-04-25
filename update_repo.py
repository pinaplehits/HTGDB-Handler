import os
from git import Repo, GitCommandError
from gitHandler import CloneProgress


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


if __name__ == "__main__":
    update_repo()
