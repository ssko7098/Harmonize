# Lab-03-Group-01

## Development Usernames and Passwords
* admin user
    * username: admin
    * password: admin
* test end user:
    * username: test
    * password: elec3609

## 1. Instructions for Installing Django
Run the command `pip install -r requirements.txt` to install all the relevant modules for this assignment.

## 2. Instructions for Accessing the Database
Before running the application, you need to ensure that all the data located in the `db_dump.json` file has been loaded into your local `db.sqlite3` file.

### 2.1 Run migrations to create the SQLite database
 Before loading data, you need to run migrations on each app to create the necessary database schema. This can be done with the command: 
 * `python3 manage.py makemigrations users music comments` and then 
 * `python3 manage.py migrate`

### 2.2 Load the data from the dump file
Once the database schema is set up, you can load the data from the dump file (`db_dump.json`) into your local `db.sqlite3` file. Run the following command: 
* `python3 manage.py loaddata db_dump.json`

### 2.3 If the above step creates a UNIQUE constraint failed
Run the following commands to fix the issue: 
* `python3 manage.py shell`
* `from django.contrib.contenttypes.models import ContentType` 
* `ContentType.objects.all().delete()`
* `exit()`
* From here, run the following again:
* `python3 manage.py loaddata db_dump.json`


### 2.4 Dumping new data
If you have added new data into the database and you want the rest of us to be able to see it, make sure you dump the new data in the `db_dump.json` file. You can do this with the following command:
* `python3 manage.py dumpdata > db_dump.json`