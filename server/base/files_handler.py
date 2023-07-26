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

def remove_file(owner, path):
    storage_folder_path = os.path.abspath(
    os.path.join(__file__, "..", "..", "..", "cloud_storage")
    )
    file_path = os.path.join(
    storage_folder_path, owner
    )
    file_path = file_path + str(path)
            
    try:
        os.remove(file_path)
        return {"message" :f"File '{path}' has been deleted successfully."}
    except FileNotFoundError:
        return {"message" :f"File '{path}' not found. Unable to delete."}
    except PermissionError:
        return {"message" :f"Permission denied. Unable to delete file '{path}'."}
    except Exception as e:
        return {"message" :f"An error occurred while deleting file '{file_path}': {str(e)}"}

