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
    # get the authentication token and use it in every request to the server.
    server_metadata = api.get_server_metadata()
    current_metadata = fh.get_all_files_metadata()
    # api.upload_new_files(current_metadata)
    # api.update_server_files(db.readall())
    # api.delete_server_files(db.readall())
    # api.get_server_files(db.readall())
    #delete_locally_deleted_files_from_server(token)
    #delete_from_local_deleted_files_on_server(token)
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


def get_conflicted_changes(server_metadata_list):
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
                        conflicted_metadata_list.append(changed_metadata)
                        break  # Break the loop if any difference is found
    return conflicted_metadata_list


def upload_locally_new_files_to_server(token):
    current_metadata = fh.get_all_files_metadata()
    new_metadata = db.get_new_metadata(current_metadata)


def delete_locally_deleted_files_from_server(token):
    current_metadata = fh.get_all_files_metadata()
    deleted_locally = db.get_removed_metadata(current_metadata)
    api.delete_server_files(deleted_locally)


def delete_from_local_deleted_files_on_server(token):
    server_metadata = api.get_server_metadata()
    deleted_on_server = db.get_removed_metadata(server_metadata)
    for item in deleted_on_server:
        full_path = str(storage_folder_path) + item["path"]
        message = fh.delete_file(full_path)
        print(message)


class Watcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        print(
            f"File {event.src_path} has been modified at:", datetime.now().isoformat()
        )

    def on_created(self, event):
        if event.is_directory:
            return
        print(f"File {event.src_path} has been created at:", datetime.now().isoformat())

    def on_deleted(self, event):
        if event.is_directory:
            return
        print(f"File {event.src_path} has been deleted at:", datetime.now().isoformat())


def watch_directory(directory_path):
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, path=directory_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


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
api = ServerApi(token=token, storage_folder_path=storage_folder_path, base_url=BASE_URL,db=db)

if __name__ == "__main__":
    main()
