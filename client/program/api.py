import requests
from pathlib import Path


class ServerApi:
    def __init__(self, token, storage_folder_path, base_url, db):
        self.token = token
        self.storage_folder_path = storage_folder_path
        self.base_url = base_url
        self.db = db
        self.token_url = base_url + "auth/"
        self.check_metadata_url = base_url + "check/"
        self.file_url = base_url + "file/"

    def upload_new_files(self, files_metadata_list):
        new_metadata = []
        print("UPLOADING NEW FILES...")
        for file_metadata in files_metadata_list:
            file_path = str(self.storage_folder_path) + file_metadata["path"]
            headers = {"Authorization": f"Token {self.token}"}
            json = {
                "name": file_metadata["name"],
                "size": file_metadata["size"],
                "hash": file_metadata["hash"],
                "path": file_metadata["path"],
            }
            with open(file_path, "rb") as file:
                files = {"file": file}
                response = requests.post(
                    self.file_url, headers=headers, data=json, files=files
                )
            metadata = response.json().get("metadata") or None
            if metadata:
                new_metadata.append(metadata)
            print("STATUS:", response.json().get("message"), "|", response.status_code)
        if new_metadata:
            self.db.insert(new_metadata)

    def get_server_metadata(self):
        headers = {"Authorization": f"Token {self.token}"}
        response = requests.get(self.check_metadata_url, headers=headers)
        server_metadata = response.json()
        return server_metadata

    def get_new_server_files(self, files_metadata_list):
        print("GETTING NEW FILES...")
        for file_metadata in files_metadata_list:
            headers = {"Authorization": f"Token {self.token}"}
            response = requests.get(
                self.file_url + str(file_metadata["id"]) + "/", headers=headers
            )
            file_path = str(self.storage_folder_path) + file_metadata["path"]
            dir_path = Path(file_path).parent
            if not dir_path.exists():
                dir_path.mkdir(parents=True)
            with open(file_path, "wb+") as destination_file:
                destination_file.write(response.content)
            print("STATUS:", file_metadata["path"], "|", response.status_code)
        self.db.insert(files_metadata_list)

    def get_updated_server_files(self, files_metadata_list):
        print("GETTING UPDATED FILES...")
        for file_metadata in files_metadata_list:
            headers = {"Authorization": f"Token {self.token}"}
            response = requests.get(
                self.file_url + str(file_metadata["id"]) + "/", headers=headers
            )
            file_path = str(self.storage_folder_path) + file_metadata["path"]
            dir_path = Path(file_path).parent
            if not dir_path.exists():
                dir_path.mkdir(parents=True)
            with open(file_path, "wb+") as destination_file:
                destination_file.write(response.content)
            print("STATUS:", file_metadata["path"], "|", response.status_code)
        self.db.update(files_metadata_list)

    def update_server_files(self, files_metadata_list):
        updated_metadata = []
        print("UPLOADING CHANGES...")
        for file_metadata in files_metadata_list:
            file_path = str(self.storage_folder_path) + file_metadata["path"]
            headers = {"Authorization": f"Token {self.token}"}
            json = {
                "name": file_metadata["name"],
                "size": file_metadata["size"],
                "hash": file_metadata["hash"],
                "path": file_metadata["path"],
            }
            with open(file_path, "rb") as file:
                files = {"file": file}
                response = requests.put(
                    self.file_url + str(file_metadata["id"]) + "/",
                    headers=headers,
                    data=json,
                    files=files,
                )
            metadata = response.json().get("metadata") or None
            if metadata:
                updated_metadata.append(metadata)
            print("STATUS:", response.json().get("message"), "|", response.status_code)
        if updated_metadata:
            self.db.update(updated_metadata)

    def delete_server_files(self, files_metadata_list):
        print("DELETING FILES...")
        for file_metadata in files_metadata_list:
            headers = {"Authorization": f"Token {self.token}"}
            response = requests.delete(
                self.file_url + str(file_metadata["id"]) + "/", headers=headers
            )
            print("STATUS:", response.json().get("message"), "|", response.status_code)
