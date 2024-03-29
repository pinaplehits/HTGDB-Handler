import logging
import os
import shutil
from configparser import ConfigParser
from gitHandler import (
    update_repo,
    git_commit_difference,
    git_commit,
    git_file_status,
    git_push,
)
from jsonHandler import (
    get_top_level_keys,
    delete_key,
    write_to_child,
    write_to_key,
    update_json_with_dict,
)
from smdbHandler import (
    get_extensions,
    read_file,
    create_new_file,
    search_value_in_key,
    remove_duplicates,
)


def load_config(section: str = "reducer", file: str = "config.ini") -> dict:
    config = ConfigParser()
    config.read(file)

    return dict(config.items(section))


def write_updated_commit(sha1: str, file: str = "config.ini") -> None:
    if not sha1:
        logging.error("No SHA1 found")
        return

    config = ConfigParser()
    config.read(file)
    config.set("reducer", "latest_reduced", sha1)

    with open(file, "w") as f:
        config.write(f)


def move_folder_to_legacy(path_master: str, path_build: str, path_legacy: str) -> None:
    try:
        if not os.path.exists(path_master) and not os.path.exists(path_build):
            raise FileNotFoundError("No master or build folder found")

        logging.info("Moving folders to legacy...")

        if os.path.exists(path_legacy):
            shutil.rmtree(path_legacy)

        if os.path.exists(path_master) and os.listdir(path_master):
            shutil.move(path_master, path_legacy)
            logging.debug("Master folder moved to legacy")
        elif os.path.exists(path_build) and os.listdir(path_build):
            shutil.move(path_build, path_legacy)
            logging.debug("Build folder moved to legacy")

        if os.path.exists(path_build):
            shutil.rmtree(path_build)
    except FileNotFoundError as e:
        logging.error(e)


def handle_modified(modified: list, updated_sha1: str, latest_sha1: str) -> None:
    if not modified:
        logging.debug("No modified files found")
        return

    json_keys = get_top_level_keys()

    verified_with_latest_sha1 = search_value_in_key(
        json_keys, "verifiedWith", latest_sha1
    )
    modified = [os.path.splitext(name)[0] for name in modified]
    keys_to_update = [key for key in verified_with_latest_sha1 if key not in modified]

    if not keys_to_update:
        logging.info("No keys to update")
        return

    update_verified_keys_with_new_sha1(updated_sha1, keys_to_update)

    logging.debug(f"Updated {len(keys_to_update)} keys with new SHA1: {updated_sha1}")


def handle_deleted(deleted: list, path: str, section: dict) -> None:
    if not deleted:
        logging.debug("No deleted files found")
        return

    basename = [os.path.splitext(name)[0] for name in deleted]

    logging.info("Removing deleted from SMDB...")
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
        logging.debug("No renamed files found")
        return

    input("Some files will be renamed, the program will end...")
    exit()


def handle_added(added: list, build_path: str, master_path: str) -> None:
    if not added:
        logging.debug("No added files found")
        return

    basename = [os.path.splitext(name)[0] for name in added]

    logging.info("Creating new folders...")
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
    logging.debug("Updating verifiedWith in db.json..")
    for key in verified_keys:
        write_to_child(key, "verifiedWith", updated_sha1)


def no_remote_changes(updated_sha1: str, latest_sha1: str) -> None:
    logging.debug("No smdb changes found")

    json_keys = get_top_level_keys()
    verified_keys = search_value_in_key(json_keys, "verifiedWith", latest_sha1)
    update_verified_keys_with_new_sha1(updated_sha1, verified_keys)


def handle_git_changes(
    git_changes: dict,
    section: dict,
    updated_sha1: str,
    latest_sha1: str,
) -> None:
    path_smdb = os.path.join(os.getcwd(), section["orig_smdb"])
    path_reduced_smdb = os.path.join(os.getcwd(), section["new_smdb"])

    handle_renamed(git_changes.get("renamed"))
    handle_added(git_changes.get("added"), section["build"], section["master"])
    handle_deleted(git_changes.get("deleted"), path_reduced_smdb, section)
    handle_modified(git_changes.get("modified"), updated_sha1, latest_sha1)

    for database in git_changes.get("added", []) + git_changes.get("modified", []):
        db_path = os.path.join(path_smdb, database)
        data = read_file(db_path)
        reduced_db = remove_duplicates(data)
        reduced_db_path = os.path.join(path_reduced_smdb, database)

        create_new_file(reduced_db_path, reduced_db)

        basename = os.path.splitext(database)[0]
        updates = {
            basename: {
                "compressed": False,
                "extensions": get_extensions(reduced_db),
                "reducedFrom": len(data),
                "reducedTo": len(reduced_db),
            }
        }
        update_json_with_dict(updates)


def process_local_changes(remote_changes: dict, local_changes: list, sha1: str) -> list:
    modified = [
        os.path.basename(change)
        for change in local_changes
        if os.path.basename(change) in remote_changes.get("modified")
    ]

    no_changes = [
        os.path.splitext(change)[0]
        for change in remote_changes.get("modified")
        if change not in modified
    ]

    update_verified_keys_with_new_sha1(sha1, no_changes)

    return modified


def reducer() -> bool:
    updated_sha1 = update_repo()
    section = load_config()
    latest_sha1 = section["latest_reduced"]

    if latest_sha1 == updated_sha1:
        return logging.info("Nothing new to reduce")

    git_changes = git_commit_difference(latest_sha1, updated_sha1)

    if not any(git_changes.values()):
        no_remote_changes(updated_sha1, latest_sha1)
    else:
        handle_git_changes(git_changes, section, updated_sha1, latest_sha1)

    write_updated_commit(updated_sha1)

    git_message = f"Reduced from {section['latest_reduced']} to {updated_sha1}"
    extra_files = ["db.json", "config.ini"]
    changes = check_git_changes(git_changes, section["new_smdb"], extra_files)

    modified = process_local_changes(git_changes, changes, updated_sha1)

    if git_commit(git_message, changes):
        git_push()

    return modified


if __name__ == "__main__":
    reducer()
