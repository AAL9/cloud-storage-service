from pathlib import Path
import os
import requests
import time
from decouple import config
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from program.db_handler import MetadataDatabase
from program.files_handler import FilesHandler

# assign the storage folder
STORAGE_FOLDER_NAME = config("STORAGE_FOLDER_NAME")

# login information
USER_NAME = config("USER_NAME")
USER_PASSWORD = config("USER_PASSWORD")

# the base URL
BASE_URL = config("BASE_URL")
# paths
token_url = BASE_URL + "auth/"
check_metadata_url = BASE_URL + "check/"
file_url = BASE_URL + "file/"

#
current_directory = Path(__file__).resolve().parent
storage_folder_path = current_directory / STORAGE_FOLDER_NAME


def main():
    check_storage_folder_exists()
    token = (
        get_token()
    )  # get the authentication token and use it in every request to the server.
    get_metadata(token)
    fh = FilesHandler(storage_folder_path)
    current_metadata = fh.get_all_files_metadata()
    db = MetadataDatabase(
        f"{STORAGE_FOLDER_NAME}.db"
    )  # establish a conncetion to the database.
    uninserted_metadata = db.get_uninserted_metadata(current_metadata)
    print("ADDITIONS MADE DURING PROGRAM OFF:")
    for item in uninserted_metadata:
        for key, value in item.items():
            print(f'"{key}" : "{value}",')
        print("------------------------------------------------------------------------------")
    changed_metadata = db.get_changed_metadata(current_metadata)
    print("MODIFICATIONS MADE DURING PROGRAM OFF:")
    for item in changed_metadata:
        for key, value in item.items():
            print(f'"{key}" : "{value}",')
        print("------------------------------------------------------------------------------")
    removed_metadata = db.get_removed_metadata(current_metadata)
    print("REMOVED FILES DURING PROGRAM OFF:")
    for item in removed_metadata:
        for key, value in item.items():
            print(f'"{key}" : "{value}",')
        print("------------------------------------------------------------------------------")
    db.delete(removed_metadata)
    #db.insert(uninserted_metadata)
    #db.update(changed_metadata)
    #db.update(current_metadata)
    
    readall_db = db.readall()
    hello = current_metadata
    print("DATABASE:")
    for item in readall_db:
        for key, value in item.items():
            print(f'"{key}" : "{value}",')
        print("------------------------------------------------------------------------------")
    #create_files(token,hello,db)
    update_files(token, changed_metadata, db)

    db.close_connection()  # close the conncetion to the database.

    # watch_directory(storage_folder_path)


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
    return token


def get_metadata(token):
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(check_metadata_url, headers=headers)
    items = response.json()
    print("ITEMS IN SERVER:")
    for item in items:
        for key, value in item.items():
            print(f'"{key}" : "{value}",')
        print("------------------------------------------------------------------------------\n")


def create_files(token, files_metadata_list, db):
    new_metadata = []
    print("UPLOADING NEW FILES...")
    for file_metadata in files_metadata_list:
        file_path = str(storage_folder_path) + file_metadata["path"]
        headers = {"Authorization": f"Token {token}"}
        json = {
            "name": file_metadata["name"],
            "size": file_metadata["size"],
            "hash": file_metadata["hash"],
            "path": file_metadata["path"],
        }
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(file_url, headers=headers, data=json, files=files)
        metadata = response.json().get("metadata") or None
        if metadata:
            new_metadata.append(metadata)
        print("STATUS:", response.json().get("message"), "|", response.status_code)
    if new_metadata:
        db.insert(new_metadata)
        


def update_files(token, files_metadata_list, db):
    updated_metadata = []
    print("UPLOADING CHANGES...")
    for file_metadata in files_metadata_list:
        file_path = str(storage_folder_path) + file_metadata["path"]
        headers = {"Authorization": f"Token {token}"}
        json = {
            "name": file_metadata["name"],
            "size": file_metadata["size"],
            "hash": file_metadata["hash"],
            "path": file_metadata["path"],
        }
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.put(file_url, headers=headers, data=json, files=files)
        metadata = response.json().get("metadata") or None
        if metadata:
            updated_metadata.append(metadata)
        print("STATUS:", response.json().get("message"), "|", response.status_code)
    if updated_metadata:
        db.update(updated_metadata)
        

















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


if __name__ == "__main__":
    main()
