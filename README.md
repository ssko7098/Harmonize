# Lab-03-Group-01

## 1. Instructions for Installing Django
Run the command `pip install -r requirements.txt` to install all the relevant modules for this assignment.

## 2. Instructions for Accessing the Database
Before running the application, you need to ensure that all the data located in the `db_dump.json` file has been loaded into your local `db.sqlite3` file.

### 2.1 Run migrations to create the SQLite database
 Before loading data, you need to run migrations on each app to create the necessary database schema. This can be done with the command: 
 * `python3 manage.py makemigrations comments music users` and then 
 * `python3 manage.py migrate`

### 2.2 Load the data from the dump file
Once the database schema is set up, you can load the data from the dump file (`db_dump.json`) into your local `db.sqlite3` file. Run the following command: 
* `python3 manage.py loaddata db_dump.json`

### 2.3 Dumping new data
If you have added new data into the database and you want the rest of us to be able to see it, make sure you dump the new data in the `db_dump.json` file. You can do this with the following command:
* `python3 manage.py dumpdata > db_dump.json`