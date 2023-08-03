import os

STORAGE_FOLDER_PATH = "/home/hp/Desktop/CloudService/cloud_storage/"


def get_file_path(owner: str, path: str):
    file_path = os.path.join(STORAGE_FOLDER_PATH, owner)
    file_path = file_path + path
    return file_path


def upload_file(owner: str, path: str, file):
    file_path = get_file_path(owner, path)
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    with open(file_path, "wb+") as destination_file:
        for chunk in file.chunks():
            destination_file.write(chunk)


def update_file(owner: str, path: str, file):
    file_path = get_file_path(owner, path)
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    with open(file_path, "wb+") as destination_file:
        for chunk in file.chunks():
            destination_file.write(chunk)


def delete_file(owner: str, path: str):
    file_path = get_file_path(owner, path)

    try:
        os.remove(file_path)
        message = f"File '{path}' has been deleted successfully."
        return message
    except FileNotFoundError:
        message = f"File '{path}' not found. Unable to delete."
        return message
    except PermissionError:
        message = f"Permission denied. Unable to delete file '{path}'."
        return message
    except Exception as e:
        message = f"An error occurred while deleting file '{path}': {str(e)}"
        return message
