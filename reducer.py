import os
import shutil
from configparser import ConfigParser
from gitHandler import (
    update_repo,
    git_difference,
    git_commit,
    git_file_status,
    git_push,
)
from jsonHandler import (
    get_top_level_keys,
    delete_key,
    write_to_child,
    write_to_key,
    find_non_empty_key,
)
from smdbHandler import (
    get_extensions,
    read_file,
    create_new_file,
    get_smdb_not_verified,
)


def load_config(section: str = "reducer", file: str = "config.ini") -> dict:
    config = ConfigParser()
    config.read(file)

    return dict(config.items(section))


def reduce_db(items: list) -> list:
    dataset = set(item[0] for item in items)

    if len(dataset) == len(items):
        print("SMDB not reduced")
        return items

    newdb = [
        item for item in items if item[0] in dataset and dataset.remove(item[0]) is None
    ]

    print(f"SMDB reduced from {len(items)} to {len(newdb)} files")

    return newdb


def write_latest_commit(sha1: str, file: str = "config.ini") -> None:
    if not sha1:
        print("No SHA1 found")
        return

    config = ConfigParser()
    config.read(file)
    config.set("reducer", "latest_reduced", sha1)

    with open(file, "w") as f:
        config.write(f)


def move_folder_to_legacy(path_master: str, path_build: str, path_legacy: str) -> None:
    if not os.path.exists(path_master) and not os.path.exists(path_build):
        print("No master or build folder found")
        return

    print("Moving folders to legacy...")

    if os.path.exists(path_legacy):
        shutil.rmtree(path_legacy)

    if os.path.exists(path_master) and os.listdir(path_master):
        shutil.move(path_master, path_legacy)
        print("Master folder moved to legacy")
    elif os.path.exists(path_build) and os.listdir(path_build):
        shutil.move(path_build, path_legacy)
        print("Build folder moved to legacy")

    if os.path.exists(path_build):
        shutil.rmtree(path_build)


def handle_modified(
    modified: list, added: list, updated_sha1: str, latest_sha1: str
) -> None:
    if not modified:
        print("No modified files found")
        return

    basename = set(os.path.splitext(name)[0] for name in modified + added)

    json_keys = get_top_level_keys()

    not_verified = get_smdb_not_verified(latest_sha1, json_keys)

    keys_to_update = [
        i for i in json_keys if i not in basename and i not in not_verified
    ]

    update_verified_keys_with_new_sha1(updated_sha1, keys_to_update)


def handle_deleted(deleted: list, path: str, section: dict) -> None:
    if not deleted:
        print("No deleted files found")
        return

    basename = [os.path.splitext(name)[0] for name in deleted]

    print("Removing deleted from SMDB...")
    for key in basename:
        delete_key(key)

        os.remove(os.path.join(path, f"{key}.txt"))

        move_folder_to_legacy(
            os.path.join(section["master"], key),
            os.path.join(section["build"], key),
            os.path.join(section["legacy"], key),
        )


def handle_renamed(renamed: list) -> None:
    if not renamed:
        print("No renamed files found")
        return

    input("Some files will be renamed, the program will end...")
    exit()


def handle_added(added: list, build_path: str, master_path: str) -> None:
    if not added:
        print("No added files found")
        return

    basename = [os.path.splitext(name)[0] for name in added]

    print("Creating new folders...")
    [
        (os.makedirs(os.path.join(path, item), exist_ok=True), write_to_key(item))
        for path in [build_path, master_path]
        for item in basename
    ]


def check_git_changes(git_changes: dict, path: str, extra_files: list = []) -> list:
    changes = [
        path + value for values in git_changes.values() for value in values if value
    ]

    changes.extend(extra_files)

    return [item for item in changes if git_file_status(item)]


def update_verified_keys_with_new_sha1(updated_sha1: str, verified_keys: list) -> None:
    print("Updating verifiedWith in db.json..")
    for key in verified_keys:
        write_to_child(key, "verifiedWith", updated_sha1)


def handle_git_changes(
    git_changes: dict,
    section: dict,
    updated_sha1: str,
    latest_sha1: str,
) -> None:
    if not any(git_changes.values()):
        print("No smdb changes found")

        verified_keys = find_non_empty_key(get_top_level_keys(), "verifiedWith")

        update_verified_keys_with_new_sha1(updated_sha1, verified_keys)
        return

    path_smdb = os.path.join(os.getcwd(), section["orig_smdb"])
    path_reduced_smdb = os.path.join(os.getcwd(), section["new_smdb"])
    handle_renamed(git_changes.get("renamed"))

    handle_added(git_changes.get("added"), section["build"], section["master"])

    handle_deleted(git_changes.get("deleted"), path_reduced_smdb, section)

    handle_modified(
        git_changes.get("modified"), git_changes.get("added"), updated_sha1, latest_sha1
    )

    for database in git_changes.get("added", []) + git_changes.get("modified", []):
        data = read_file(os.path.join(path_smdb, database))
        basename = os.path.splitext(database)[0]
        newdb = reduce_db(data)

        create_new_file(os.path.join(path_reduced_smdb, database), newdb)
        write_to_child(basename, "extensions", get_extensions(newdb))
        write_to_child(basename, "reducedTo", len(newdb))
        write_to_child(basename, "reducedFrom", len(data))
        write_to_child(basename, "compressed", False)


def reducer() -> None:
    updated_sha1 = update_repo()
    section = load_config()
    latest_sha1 = section["latest_reduced"]

    if latest_sha1 == updated_sha1:
        return print("Nothing new to reduce")

    git_changes = git_difference(latest_sha1, updated_sha1)

    handle_git_changes(git_changes, section, updated_sha1, latest_sha1)

    write_latest_commit(updated_sha1)

    git_message = f"Reduced from {section['latest_reduced']} to {updated_sha1}"
    extra_files = ["db.json", "config.ini"]
    changes = check_git_changes(git_changes, section["new_smdb"], extra_files)

    git_commit(git_message, changes)
    git_push()


if __name__ == "__main__":
    reducer()
