import git

repo = git.Repo("Hardware-Target-Game-Database")

# get the two commit objects to compare
commit1 = repo.commit("e55970d")
commit2 = repo.commit("27bd299")

# get the differences between the two commits
diff = commit1.diff(commit2)

# iterate over the differences and extract the file names
changed_files = []
new_files = []
deleted_files = []

for d in diff:
    if d.a_blob is None:
        # file is new in second commit
        new_files.append(d.b_blob.path)
    elif d.b_blob is None:
        # file is deleted in second commit
        deleted_files.append(d.a_blob.path)
    else:
        # file is modified or renamed
        changed_files.append(d.b_blob.path)

print(changed_files)
print(new_files)
print(deleted_files)
