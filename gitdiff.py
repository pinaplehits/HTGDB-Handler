import git
import json
import os

repo = git.Repo("Hardware-Target-Game-Database")

# get the two commit objects to compare
old_commit = repo.commit("HEAD~150")
new_commit = repo.commit("HEAD")

# get the differences between the two commits
index = old_commit.diff(new_commit)

changes = {"add": [], "delete": [], "modified": [], "renamed": []}

# iterate over the differences and print the file names
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


# convert the dictionary of changes to a JSON string
changes_json = json.dumps(changes, indent=2)

# print the JSON string
print(changes_json)
