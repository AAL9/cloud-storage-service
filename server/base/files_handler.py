import os

def get_all_files_dirs(directory_path, file_list=None):
    root_dir = ''
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
        file_list = [path.replace(root_dir, '') for path in file_list]
    return file_list