# Lab-03-Group-01

## 1. Instructions for Running
Before running the application, you need to ensure that all the data located in the `db_dump.json` file has been loaded into your local `db.sqlite3` file.

### 1.1 Run migrations to create the SQLite database
 Before loading data, you need to run migrations on each app to create the necessary database schema. This can be done with the command: `python3 manage.py migrate`

### 1.2 Load the data from the dump file
Once the database schema is set up, you can load the data from the dump file (`db_dump.json`) into your local `db.sqlite3` file. Run the following command: `python3 manage.py loaddata db_dump.json`

