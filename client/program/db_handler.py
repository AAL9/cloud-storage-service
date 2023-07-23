import sqlite3

class MetadataDatabase:
    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            updated_at TEXT,
            hash TEXT NOT NULL,
            path TEXT NOT NULL,
            size INTEGER NOT NULL
        );
        '''
        cursor.execute(create_table_query)
    def validate_data(self, data):
        required_keys = ['name', 'hash', 'path', 'size']
        for entry in data:
            for key in required_keys:
                if key not in entry:
                    raise ValueError(f"Missing required key '{key}' in metadata entry")
            
            if not isinstance(entry['name'], str):
                raise ValueError("The 'name' value should be a string")
            
            if 'updated_at' in entry and not isinstance(entry['updated_at'], str):
                raise ValueError("The 'updated_at' value should be a string")
            
            if not isinstance(entry['hash'], str):
                raise ValueError("The 'hash' value should be a string")
            
            if not isinstance(entry['path'], str):
                raise ValueError("The 'path' value should be a string")
            
            if not isinstance(entry['size'], int):
                raise ValueError("The 'size' value should be an integer")


    def insert(self, file_metadata):
        cursor = self.conn.cursor()
        insert_data_query = '''
        INSERT INTO metadata (name, updated_at, hash, path, size) VALUES (?, ?, ?, ?, ?)
        '''
        data_to_insert = []

        for item in file_metadata:
            updated_at = item.get('updated_at', None)  # Get 'updated_at' if provided, otherwise use empty string
            data_to_insert.append((item['name'], updated_at, item['hash'], item['path'], item['size']))

        cursor.executemany(insert_data_query, data_to_insert)
        self.conn.commit()

    def readall(self):
        cursor = self.conn.cursor()
        select_query = '''
        SELECT * FROM metadata
        '''
        cursor.execute(select_query)
        column_names = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        data_list = []
        for row in rows:
            data_dict = dict(zip(column_names[1:], row[1:]))
            data_list.append(data_dict)
        return data_list
    
    def delete(self, file_path):
        cursor = self.conn.cursor()
        delete_query = '''
        DELETE FROM metadata WHERE path=?
        '''
        cursor.execute(delete_query, (file_path,))
        self.conn.commit()

    def update(self, updated_data_list):
        cursor = self.conn.cursor()
        for updated_data in updated_data_list:
            file_path = updated_data['path']
            select_query = '''
            SELECT updated_at, name, hash, size FROM metadata WHERE path=?
            '''
            cursor.execute(select_query, (file_path,))
            existing_data = cursor.fetchone()

            if not existing_data:
                raise ValueError(f"Metadata not found for path: {file_path}")

            existing_updated_at, existing_name, existing_hash, existing_size = existing_data

            updated_name = updated_data.get('name', existing_name)
            updated_hash = updated_data.get('hash', existing_hash)
            updated_size = updated_data.get('size', existing_size)
            updated_updated_at = updated_data.get('updated_at', existing_updated_at)
            
            update_query = '''
            UPDATE metadata SET name=?, updated_at=?, hash=?, size=? WHERE path=?
            '''
            updated_data_with_path = (updated_name, updated_updated_at, updated_hash, updated_size, file_path)

            cursor.execute(update_query, updated_data_with_path)
        self.conn.commit()
    
    def get_uninserted_metadata(self, file_metadata_list):
        cursor = self.conn.cursor()

        uninserted_metadata = []

        for item in file_metadata_list:
            file_path = item['path']

            select_query = '''
            SELECT path FROM metadata WHERE path=?
            '''
            cursor.execute(select_query, (file_path,))
            existing_path = cursor.fetchone()

            if not existing_path:
                uninserted_metadata.append(item)

        return uninserted_metadata

    def get_changed_metadata(self, file_metadata_list):
        cursor = self.conn.cursor()
        changed_metadata = []
        for current_item in file_metadata_list:
            file_path = current_item['path']

            select_query = '''
            SELECT * FROM metadata WHERE path=?
            '''

            cursor.execute(select_query,(file_path,))
            db_item = cursor.fetchone()
            if not db_item:
                # If the item is not found in the database, consider it as changed
                changed_metadata.append(current_item)
            else:
                column_names = [column[0] for column in cursor.description]
                db_item_dict = dict(zip(column_names, db_item))
                for key in current_item.keys():
                    if current_item[key] != db_item_dict[key]:
                        # If any attribute is different, consider it as changed
                        changed_metadata.append(current_item)
                        break  # Break the loop if any difference is found
        return changed_metadata

            


    def close_connection(self):
        self.conn.close()