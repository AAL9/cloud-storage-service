import os

from CloudService.settings import STORAGE_FOLDER_PATH 


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
    except FileNotFoundError as e:
        raise e
    except PermissionError as e:
        raise e
    except Exception as e:
        raise e
