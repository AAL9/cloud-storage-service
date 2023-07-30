from pathlib import Path
import requests
import time
from decouple import config
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from program.db_handler import MetadataDatabase
from program.files_handler import FilesHandler
from program.api import ServerApi


def main():
    check_storage_folder_exists()
    try:
        while True:
            time.sleep(1)
            # delete any file that have been deleted on either sides, locally or on server.
            delete_from_local_deleted_files_on_server()
            delete_locally_deleted_files_from_server()

            # get new files in the server
            server_metadata = api.get_server_metadata()
            new_server_metadata = db.get_new_metadata(server_metadata)
            if new_server_metadata:
                api.get_new_server_files(new_server_metadata)

            # send new files
            current_metadata = fh.get_all_files_metadata()
            new_metadata = db.get_new_metadata(current_metadata)
            if new_metadata:
                api.upload_new_files(new_metadata)

            # send the updates to the server
            send_locally_updated_files_to_server()

            # get latest changes happened on the server's files
            get_changes_on_server()

    except KeyboardInterrupt:
        pass
    db.close_connection()  # close the conncetion to the database.


def check_storage_folder_exists():
    if not (storage_folder_path.exists() and storage_folder_path.is_dir()):
        raise FileNotFoundError(
            f"The {STORAGE_FOLDER_NAME} folder does not exist in the current directory."
        )


def get_token():
    response = requests.post(
        token_url,
        json={
            "username": USER_NAME,
            "password": USER_PASSWORD,
        },
    )
    token = response.json().get("token")
    print("Successful authentication!")
    return token


def get_conflicted_changes():
    server_metadata_list = api.get_server_metadata()
    conflicted_metadata_list = []
    current_metadata = fh.get_all_files_metadata()
    changed_metadata_list = db.get_changed_metadata(current_metadata)
    for changed_metadata in changed_metadata_list:
        for server_metadata in server_metadata_list:
            if server_metadata.get("path") == changed_metadata["path"]:
                changed_metadata_from_db = db.read(changed_metadata["path"])
                for key in changed_metadata.keys():
                    if changed_metadata_from_db[key] != server_metadata[key]:
                        # If any attribute is different, consider it as changed
                        conflicted_metadata_list.append(server_metadata)
                        break  # Break the loop if any difference is found
    return conflicted_metadata_list


def get_changes_on_server():
    change_on_server_list = []
    current_metadata_list = fh.get_all_files_metadata()
    server_metadata_list = api.get_server_metadata()
    for current_metadata in current_metadata_list:
        for server_metadata in server_metadata_list:
            if server_metadata.get("path") == current_metadata["path"]:
                for key in current_metadata.keys():
                    if current_metadata[key] != server_metadata[key]:
                        metadata_from_db = db.read(current_metadata["path"])
                        if metadata_from_db[key] == current_metadata[key]:
                            change_on_server_list.append(server_metadata)
                            break
                break
    if change_on_server_list:
        api.get_updated_server_files(change_on_server_list)


def send_locally_updated_files_to_server():
    current_metadata = fh.get_all_files_metadata()
    locally_changed_metadata = db.get_changed_metadata(current_metadata)
    conflicted_changes = get_conflicted_changes()
    if conflicted_changes:
        print(
            f'ALERT: you have "{len(conflicted_changes)}" conflicted changes!\n You need to resolve these conflicts!'
        )
        update_list = []
        get_list = []
        for conflict_item in conflicted_changes:
            print(f'choose an action to resolve conflict in "{conflict_item["path"]}":')
            print("[1] force local change on the server.")
            print("[2] discard local changes and get latest server update.")
            print(
                "[3] get latest server version and resolve conflict manually. (NOTE: before choosing this option, you need to have a copy of the file contains the local changes outside the storage folder)"
            )

            valid_choices = {"1", "2", "3"}
            choice = None

            while choice not in valid_choices:
                choice = input("CHOOSE:")

            if choice == "1":
                update_list.append(conflict_item)
            elif choice == "2":
                get_list.append(conflict_item)
            elif choice == "3":
                get_list.append(conflict_item)
            else:
                raise ValueError("Invalid choice. Please choose 1, 2, or 3.")
        if get_list:
            api.get_updated_server_files(get_list)
        if update_list:
            api.update_server_files(update_list)
    else:
        if locally_changed_metadata:
            api.update_server_files(locally_changed_metadata)


def delete_locally_deleted_files_from_server():
    current_metadata = fh.get_all_files_metadata()
    deleted_locally = db.get_removed_metadata(current_metadata)
    if deleted_locally:
        api.delete_server_files(deleted_locally)
        db.delete(deleted_data_list=deleted_locally)


def delete_from_local_deleted_files_on_server():
    server_metadata = api.get_server_metadata()
    deleted_on_server = db.get_removed_metadata(server_metadata)
    if deleted_on_server:
        for item in deleted_on_server:
            item["path"]
            message = fh.delete_file(item["path"])
            print(message)
        db.delete(deleted_data_list=deleted_on_server)


# assign the storage folder
STORAGE_FOLDER_NAME = config("STORAGE_FOLDER_NAME")

# login information
USER_NAME = config("USER_NAME")
USER_PASSWORD = config("USER_PASSWORD")

# the base URL
BASE_URL = config("BASE_URL")
# urls
token_url = BASE_URL + "auth/"
check_metadata_url = BASE_URL + "check/"
file_url = BASE_URL + "file/"
token = get_token()
# the storage folder full path
storage_folder_path = Path(__file__).resolve().parent / STORAGE_FOLDER_NAME

# Database connection
db = MetadataDatabase(f"{STORAGE_FOLDER_NAME}.db")

# files handler
fh = FilesHandler(storage_folder_path)

# api
api = ServerApi(
    token=token, storage_folder_path=storage_folder_path, base_url=BASE_URL, db=db
)

if __name__ == "__main__":
    main()
