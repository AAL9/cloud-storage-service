from pathlib import Path
import requests
from decouple import config

# assign the storage folder
STORAGE_FOLDER_NAME = config('STORAGE_FOLDER_NAME')

# login information
USER_NAME = config('USER_NAME')
USER_PASSWORD = config('USER_PASSWORD')

# the base URL
BASE_URL = config('BASE_URL')
#paths
token_url = BASE_URL + "auth/"
dir_url = BASE_URL + "dir/"


current_directory = Path(__file__).resolve().parent
target_folder_path = current_directory / STORAGE_FOLDER_NAME


def main():
    check_storage_folder_exists()
    token = get_token()
    

def check_storage_folder_exists():
    if not (target_folder_path.exists() and target_folder_path.is_dir()):
        raise FileNotFoundError(f"The {STORAGE_FOLDER_NAME} folder does not exist in the current directory.")

def get_token():
    response = requests.post(token_url, json={
        'username' : USER_NAME,
        'password' : USER_PASSWORD, 
    })
    token = response.json()['token']
    return token

if __name__ == "__main__":
    main()