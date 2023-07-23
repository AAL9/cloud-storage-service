import hashlib

def calculate_file_hash(file_path, hash_algorithm="sha256"):
    # Specify the hash algorithm to use (default is SHA-256)
    hash_obj = hashlib.new(hash_algorithm)

    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        # Read the file in chunks to avoid reading the whole file into memory
        chunk_size = 4096  # You can adjust the chunk size based on your needs
        while chunk := file.read(chunk_size):
            hash_obj.update(chunk)

    # Get the hashed value as a hexadecimal string
    file_hash = hash_obj.hexdigest()

    return file_hash