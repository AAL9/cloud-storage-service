from pathlib import Path
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
# urls
token_url = BASE_URL + "auth/"
check_metadata_url = BASE_URL + "check/"
file_url = BASE_URL + "file/"

# the storage folder full path
storage_folder_path = Path(__file__).resolve().parent / STORAGE_FOLDER_NAME

# Database connection
db = MetadataDatabase(f"{STORAGE_FOLDER_NAME}.db")

# files handler
fh = FilesHandler(storage_folder_path)


def main():
    check_storage_folder_exists()
    token = (
        get_token()
    )  # get the authentication token and use it in every request to the server.
    server_metadata = get_server_metadata(token)
    current_metadata = fh.get_all_files_metadata()
    #create_files(token, current_metadata)
    #update_files(token,db.readall())
    #delete_files(token, db.readall())
    #get_files(token ,db.readall())
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
    return token


def get_server_metadata(token):
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(check_metadata_url, headers=headers)
    server_metadata = response.json()
    return server_metadata


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


def get_files(token, files_metadata_list):
    print("GETTING FILES...")
    for file_metadata in files_metadata_list:
        headers = {"Authorization": f"Token {token}"}
        response = requests.get(
            file_url + str(file_metadata["id"]) + "/", headers=headers
        )
        file_path = str(storage_folder_path) + file_metadata["path"]
        dir_path = Path(file_path).parent
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
        with open(file_path, "wb+") as destination_file:
            destination_file.write(response.content)
        print("STATUS:", file_metadata["path"], "|", response.status_code)



def create_files(token, files_metadata_list):
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


def update_files(token, files_metadata_list):
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
            response = requests.put(
                file_url + str(file_metadata["id"]) + "/",
                headers=headers,
                data=json,
                files=files,
            )
        metadata = response.json().get("metadata") or None
        if metadata:
            updated_metadata.append(metadata)
        print("STATUS:", response.json().get("message"), "|", response.status_code)
    if updated_metadata:
        db.update(updated_metadata)


def delete_files(token, files_metadata_list):
    print("DELETING FILES...")
    for file_metadata in files_metadata_list:
        headers = {"Authorization": f"Token {token}"}
        response = requests.delete(
            file_url + str(file_metadata["id"]) + "/", headers=headers
        )
        print("STATUS:", response.json().get("message"), "|", response.status_code)


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
