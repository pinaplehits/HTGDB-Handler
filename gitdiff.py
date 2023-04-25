import git
import json
import os

repo = git.Repo("Hardware-Target-Game-Database")

old_commit = repo.commit("HEAD~150")
new_commit = repo.commit("HEAD")

index = old_commit.diff(new_commit)

changes = {"add": [], "delete": [], "modified": [], "renamed": []}

for item in index:
    is_new_smdb = item.b_path.startswith(
        "EverDrive Pack SMDBs"
    ) and item.b_path.endswith(".txt")
    is_deleted = item.change_type == "D"
    is_modified = item.change_type == "M"
    is_added = item.change_type == "A"
    is_renamed = item.change_type == "R"

    if is_new_smdb:
        if is_deleted:
            changes["delete"].append(os.path.basename(item.a_blob.path))
        elif is_modified:
            changes["modified"].append(os.path.basename(item.b_blob.path))
        elif is_added:
            changes["add"].append(os.path.basename(item.b_blob.path))
        elif is_renamed:
            changes["renamed"].append(
                {
                    "from": os.path.basename(item.a_blob.path),
                    "to": os.path.basename(item.b_blob.path),
                }
            )


changes_json = json.dumps(changes, indent=2)

print(changes_json)
