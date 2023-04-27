from git import Repo
import json
import os

repo = Repo("Hardware-Target-Game-Database")

old_commit = repo.commit("HEAD~50")
new_commit = repo.commit("HEAD")

index = old_commit.diff(new_commit)

changes = {"add": [], "delete": [], "modified": [], "renamed": []}

for item in index:
    if item.b_path.startswith("EverDrive Pack SMDBs") and item.b_path.endswith(".txt"):
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

changes_json = json.dumps(changes, indent=2)

print(changes_json)
