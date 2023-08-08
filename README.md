# Welcome!
Hi! This project is a cloud storage system. it has a **server** and a **client**. the server is **Django REST Framework**.  The client is just a few Python scripts.

# How does it work?
You have a **client** that assigns a folder to be the storage folder. Then, it connects to the server. And just like that, you have a shared folder with the cloud. Anything in this folder will be uploaded to the cloud (the server). Also, any other **client** that logs in with the same credentials will have the same folder's content. Also, any file in that folder that have been created, updated, or deleted, will be modified on every client that uses the same credentials. In simple words, a shared folder!!!

# Install & Setup
> #### prerequisites:
> - Poetry
> - Git
> - PostgreSQL
### Step 1, download the project from GitHub:
First, create a new folder and open the terminal in that folder. Then, run this command:
```
git clone https://github.com/AAL9/cloud-storage-service.git
```
### Step 2, setup the database:
1. First, run the following command to switch to the **postgres**  user and open the **psql** command-line interface for working with PostgreSQL.
```
$ sudo -u postgres psql
```
This will log you into an interactive PostgreSQL session.

2. Once you are logged into PostgreSQL, the next step is to create a database for the Django app, and you can call it whatever you want, but in this case, let us call it  **metadataDB**.

```
CREATE DATABASE metadataDB;

```

3. Then, create a user that controls the database, and run the following query to create a new user called  **admin**. Again, you can replace  **admin** with a name of your choice.

```
CREATE USER admin WITH PASSWORD 'pa$$word';

```

4. Run the following query to give your user (**admin**) full access to the  **metadataDB** database, including creating new tables and documents.

```
GRANT ALL PRIVILEGES ON DATABASE metadataDB TO admin;

```

5. Next, modify a few of the connection settings for your user to speed up database operations.

```
ALTER ROLE admin SET client_encoding TO 'utf8';

ALTER ROLE admin SET default_transaction_isolation TO 'read committed';

ALTER ROLE admin SET timezone TO 'UTC';

```
6. Finally, exit the SQL prompt using the following command:
```
\q
```
With the database configured, it is time to set up your development environment.
### Step 3, setup the server:
1. First, navigate your way to the folder **CloudService** then, make a copy of the file **.envexample** and rename it to **.env**. After that, enter the file **.env**, and you should have something like this:
```
SECRET_KEY=
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASS=
STORAGE_FOLDER_PATH=
```
Fill in the variables:
```
SECRET_KEY=TheSecretKey
DATABASE_NAME=metadatadb
DATABASE_USER=admin
DATABASE_PASS=pa$$word
STORAGE_FOLDER_PATH=/home/hp/Desktop/storages/server_storage

```
2. Navigate your way to the **server** folder, then open the terminal and run this command:
```
$ poetry install
```
This command should install all dependencies needed inside a virtual environment for the server.

3. On the same terminal in the previous step, run this command that shall **activate** the virtual environment:
```
$ poetry shell
```
You should have something like this in the terminal:
```
(server-py3.10) $
```
4. Then, migrate all models:
```
(server-py3.10)$ python manage.py migrate
```
5. Now, **create** a user by running this command:
```
$ python manage.py createsuperuser
```

### Step 4, setup the client:
1. Now, navigate to the **client** directory and make a copy of the file **.envexample** and rename it to **.env**. After that, enter the file **.env**, and you should have something like this:
```
USER_NAME=
USER_PASSWORD=
BASE_URL=
STORAGE_FOLDER_PATH=
```
Fill in the variables:
```
USER_NAME=admin
USER_PASSWORD=pa$$word
BASE_URL=http://127.0.0.1:8000/
STORAGE_FOLDER_PATH=/home/hp/Desktop/storages/client_storage
```
2. Then, open a terminal there and run this command:
```
$ poetry install 
```
# Running the server and the client
### Running the server:
1. Navigate your way to the **server** directory and open a terminal, then run this command to activate the virtual environment: 
```
$ poetry shell
```
2. After activating the virtual environment, run this command to run the server:
```
(server-py3.10) $ python manage.py runserver
```
Now, you have the server up and running!!!
### Running the client:
1. Navigate your way to the  **client** directory, then run this command to activate the virtual environment:
```
poetry shell
```
You should have something like this in the terminal:
```
(client-py3.10) $
```
After that, run the **`client.py`**:
```
(client-py3.10) $ python3 client.py
```
Now, your **storage folder** is connected to the server, and anything in that folder will be uploaded to the server, and anyone with the same credentials will have the same folder as you have... how exciting!!!

