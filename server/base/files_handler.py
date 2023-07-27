import os


def get_all_files_dirs(directory_path, file_list=None):
    root_dir = ""
    if file_list is None:
        root_dir = directory_path
        file_list = []

    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            file_list.append(item_path + "/")
            if os.listdir(item_path):
                get_all_files_dirs(item_path, file_list)
        else:
            file_list.append(item_path)
    if root_dir == directory_path:
        file_list = [path.replace(root_dir, "") for path in file_list]
    return file_list


def upload_file(owner: str, path: str, file):
    storage_folder_path = os.path.abspath(
        os.path.join(__file__, "..", "..", "..", "cloud_storage")
    )
    file_path = os.path.join(storage_folder_path, owner)
    file_path = file_path + path
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    with open(file_path, "wb+") as destination_file:
        for chunk in file.chunks():
            destination_file.write(chunk)


def update_file(owner: str, path: str, file):
    storage_folder_path = os.path.abspath(
        os.path.join(__file__, "..", "..", "..", "cloud_storage")
    )
    file_path = os.path.join(storage_folder_path, owner)
    file_path = file_path + path
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    with open(file_path, "wb+") as destination_file:
        for chunk in file.chunks():
            destination_file.write(chunk)


def delete_file(owner: str, path: str):
    storage_folder_path = os.path.abspath(
        os.path.join(__file__, "..", "..", "..", "cloud_storage")
    )
    file_path = os.path.join(storage_folder_path, owner)
    file_path = file_path + path

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
        message = f"An error occurred while deleting file '{file_path}': {str(e)}"
        return message
