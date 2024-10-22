# Harmonize: A Music Streaming Platform

## Table of Contents
- [Project Overview](#project-overview)
- [Installation Instructions](#installation-instructions)
- [Configuration and Environment Setup](#configuration-and-environment-setup)
- [Usage Instructions](#usage-instructions)
- [API Documentation](#api-documentation)
- [Known Issues](#known-issues)

## Project Overview
Our project `Harmonize` aims to develop a robust and user-friendly music streaming platform, providing essential features for both users and administrators. The core objectives include creating a secure and interactive environment where users can listen to music, manage playlists, and engage with other users through profile comments, while admins efficiently curate content and oversee user management.

### Key Features:
* __User Authentication:__ Critical for distinguishing between normal and admin users. This feature enables customized experiences and account-specific functions like profile pages with user interactions through comments.
* __Music Library Access:__ Users can browse and listen to a database of songs, forming the foundation of the platform's identity as a music streaming service.
* __Playlist Management:__ Users can create, manage, and organize personal playlists, making music discovery and enjoyment seamless.
*Playback Controls: Standard controls like rewind, skip, and pause ensure a smooth listening experience.
* __Profile Comment Section:__ A unique feature where users can leave and receive comments, fostering community engagement around their favorite artists.
* __Admin Privileges:__ Admins can manage content by adding, deleting, and updating songs and user accounts, essential for platform curation.

## Installation Instructions

### 1. Install Dependencies
Install all the necessary packages using the requirements file:
```bash
pip install -r requirements.txt
```

### 2. Instructions for Accessing the Database
Before running the application, you need to ensure that all the data located in the `db_dump.json` file has been loaded into your local `db.sqlite3` file.

#### 2.1 Run migrations
To create the necessary database schema, run:
```bash
python3 manage.py makemigrations users music comments
python3 manage.py migrate
```

#### 2.2 Load the data from the dump file
Once the database schema is set up, you can load the data from the dump file (`db_dump.json`) into your local `db.sqlite3` file. Run the following command: 
``` bash
python3 manage.py loaddata db_dump.json
```

If you encounter a `UNIQUE constraint failed` error, follow these steps: 
``` bash
python3 manage.py shell
from django.contrib.contenttypes.models import ContentType
ContentType.objects.all().delete()
exit()
python3 manage.py loaddata db_dump.json
```

#### 2.3 Dump new data (Optional)
If you have added new data and want to share it, dump the data:
```bash
python3 manage.py dumpdata > db_dump.json
```

### 3. Run the Development Server
```bash
python3 manage.py runserver
```

### 4. Instructions for Accessing sqlite CLI (Optional)
__NOTE:__ Before running the below code in the terminal, make sure to `cd` into the `mysite` directory.

Run the following code to access the CLI for sqlite:
```bash
sqlite3 -init config.sql db.sqlite3
```

## Configuration and Environment Setup
### Environment Variables
Create a `.env` file in the project root directory to store sensitive environment variables:
* `SECRET_KEY`: A unique key for Django security.
* `DEBUG`: Set to True for local development.
* `ALLOWED_HOSTS`: Specify the domain names allowed to access the app.


## Usage Instructions
### Running the application
1. Ensure the development server is running:
```bash
python3 manage.py runserver
```

2. Access the applicaiton in your browser at `http://127.0.0.1:8000/`

### Development Usernames and Passwords
* admin user
    * username: admin
    * password: admin
* test end user:
    * username: test
    * password: elec3609

## API Documentation
### Available Endpoints

## Known Issues
### Current Issues
* __Auto Fill Styling Issue:__ When the user auto-fills forms like the login page, it causes a styling issue where the form turns white.

### Planned Features
* __Offline Listening:__ Ability for users to download songs and listen offline.
* __Music Recommendations:__ Suggest songs to users based on their location and what others around them are listening to.
