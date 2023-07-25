import hashlib
import os


class FilesHandler:
    def __init__(self, storage_directory):
        self.storage_directory = storage_directory

    def get_all_files_metadata(self):
        file_list = []
        self._get_all_files_metadata_recursive(self.storage_directory, file_list)
        file_list = [
            {**item, "path": item["path"].replace(str(self.storage_directory), "")}
            for item in file_list
        ]
        return file_list

    def _get_all_files_metadata_recursive(self, directory_path, file_list):
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path) and (os.listdir(item_path) is not None):
                self._get_all_files_metadata_recursive(item_path, file_list)
            else:
                item_size = os.path.getsize(item_path)
                item_hash = self.calculate_file_hash(item_path)
                item_info = {
                    "name": item,
                    "hash": item_hash,
                    "path": item_path,
                    "size": item_size,
                }
                file_list.append(item_info)

    def calculate_file_hash(self, file_path, hash_algorithm="sha256"):
        # Specify the hash algorithm to use (default is SHA-256)
        hash_obj = hashlib.new(hash_algorithm)

        # Open the file in binary mode
        with open(file_path, "rb") as file:
            # Read the file in chunks to avoid reading the whole file into memory
            chunk_size = 4096  # You can adjust the chunk size based on your needs
            while chunk := file.read(chunk_size):
                hash_obj.update(chunk)

        # Get the hashed value as a hexadecimal string
        file_hash = hash_obj.hexdigest()

        return file_hash
