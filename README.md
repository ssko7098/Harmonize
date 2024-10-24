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
* __Playback Controls:__ Standard controls like rewind, skip, and pause ensure a smooth listening experience.
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
sqlite3 db.sqlite3
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

# API Documentation

## Available Endpoints

### 1. User Playlists

1. **`GET /music/playlists/{username}/`**
   - **Description**: Retrieves all playlists created by a specific user.
   - **Permissions**: Only the authenticated user can view their own playlists.
   - **Request Parameters**: 
     - `username` (string): The username whose playlists to retrieve.
   - **Response**:
     - **200 OK**: Returns a list of playlists belonging to the user.
     - **403 Forbidden**: If the authenticated user tries to view someone else's playlists.
     - **404 Not Found**: Indicates that the requested resource could not be found on the server.


2. **`POST /music/playlists/create/`**
   - **Description**: Creates a new playlist for the authenticated user.
   - **Permissions**: Only authenticated users can create playlists.
   - **Request Body**: 
     - `name` (string): The name of the playlist.
     - `description` (string, optional): A description of the playlist.
   - **Response**:
     - **201 Created**: Playlist is successfully created.
     - **400 Bad Request**: If the request body is invalid.

3. **`DELETE /music/playlists/{playlist_id}/remove/`**
   - **Description**: Deletes a playlist created by the authenticated user.
   - **Permissions**: Only the owner of the playlist can delete it.
   - **Request Parameters**:
     - `playlist_id` (int): The ID of the playlist to delete.
   - **Response**:
     - **204 No Content**: Playlist successfully deleted.
     - **403 Forbidden**: If the authenticated user tries to delete someone else's playlist.
     - **404 Not Found**: Indicates that the requested resource could not be found on the server.


4. **`PUT /music/playlists/{playlist_id}/update/`**
   - **Description**: Updates a specific playlist's details.
   - **Permissions**: Only the owner of the playlist can update it.
   - **Request Parameters**:
     - `playlist_id` (int): The ID of the playlist to update.
   - **Request Body**:
     - `name` (string): Updated name of the playlist.
     - `description` (string, optional): Updated description of the playlist.
   - **Response**:
     - **200 OK**: Playlist updated successfully.
     - **400 Bad Request**: If the update data is invalid.
     - **403 Forbidden**: If the authenticated user tries to update someone else's playlist.
     - **404 Not Found**: Indicates that the requested resource could not be found on the server.


---

### 2. Songs in Playlist

1. **`GET /music/playlists/{playlist_id}/songs/`**
   - **Description**: Retrieves all songs in a specific playlist.
   - **Permissions**: Only the owner of the playlist can view the songs.
   - **Request Parameters**:
     - `playlist_id` (int): The ID of the playlist to retrieve songs from.
   - **Response**:
     - **200 OK**: Returns a list of songs in the playlist.
     - **403 Forbidden**: If the authenticated user tries to view someone else's playlist.
     - **404 Not Found**: Indicates that the requested resource could not be found on the server.

2. **`POST /music/playlists/{playlist_id}/songs/{song_id}/add/`**
   - **Description**: Adds a song to a playlist.
   - **Permissions**: Only the owner of the playlist can add songs.
   - **Request Parameters**:
     - `playlist_id` (int): The ID of the playlist.
     - `song_id` (int): The ID of the song to add.
   - **Response**:
     - **201 Created**: Song successfully added to the playlist.
     - **400 Bad Request**: If the song is already in the playlist or request is invalid.
     - **403 Forbidden**: If the authenticated user tries to modify someone else's playlist.
     - **404 Not Found**: Indicates that the requested resource could not be found on the server.


3. **`DELETE /music/playlists/{playlist_id}/songs/{song_id}/remove/`**
   - **Description**: Removes a song from a playlist.
   - **Permissions**: Only the owner of the playlist can remove songs.
   - **Request Parameters**:
     - `playlist_id` (int): The ID of the playlist.
     - `song_id` (int): The ID of the song to remove.
   - **Response**:
     - **204 No Content**: Song successfully removed from the playlist.
     - **403 Forbidden**: If the authenticated user tries to modify someone else's playlist.
     - **404 Not Found**: Indicates that the requested resource could not be found on the server.


---

### 3. Authentication & CSRF

1. **`GET /music/get-csrf/`**
   - **Description**: Retrieves the CSRF token required for POST, PUT, and DELETE requests.
   - **Permissions**: Open to any user.
   - **Response**:
     - **200 OK**: Returns the CSRF token in JSON format.
   
2. **Authentication**
   - **Bearer Token**: For any protected routes, users must pass the JWT token in the `Authorization` header:
    **Request:**
    ```bash
    POST /api/token/
    Content-Type: application/json

    ```
    **Request Body:**
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```

    **Response:**
    ```json
    {
        "access": "your_access_token",
        "refresh": "your_refresh_token"
    }

    ```

     ```
     Authorization: Bearer <your_token>
     ```

---

### 4. Example of API Request & Response

1. **Create Playlist Example**

    **Request:**
    ```bash
    POST /music/playlists/create/
    Authorization: Bearer <your_token>
    Content-Type: application/json
    ```
    **Request Body:**
    ```json
    {
      "name": "Chill Vibes",
      "description": "A playlist of relaxing songs."
    }
    ```

    **Response:**
    ```json
    {
      "message": "Playlist created successfully."
    }
    ```

2. **Add Song to Playlist Example**

    **Request:**
    ```bash
    POST /music/playlists/1/songs/5/add/
    Authorization: Bearer <your_token>
    Content-Type: application/json
    ```

    **Response:**
    ```json
    {
      "message": "Song added to playlist successfully."
    }
    ```
3. **Remove Playlist Example**

    **Request:**
    ```bash
    DELETE /music/playlists/1/remove/
    Authorization: Bearer <your_token>

    ```

    **Response:**
    ```json
    {
        "message": "Playlist removed successfully."
    }

    ```
4. **Update Playlist Example**

    **Request:**
    ```bash
    PUT /music/playlists/1/update/
    Authorization: Bearer <your_token>
    Content-Type: application/json

    ```

    **Request Body:**
    ```json
    {
        "name": "Updated Playlist Name",
        "description": "Updated description."
    }

    ```

    **Response:**
    ```json
    {
        "message": "Playlist updated successfully."
    }


    ```
5. **View User Playlist Example**

    **Request:**
    ```bash
    GET /music/playlists/dim/
    Authorization: Bearer <your_token>
    ```

    **Response:**
    ```json
    [
    {
        "playlist_id": 1,
        "name": "Chill Vibes",
        "description": "A playlist of relaxing songs.",
        "report_count": 0,
        "songs": []
    }
    ]

    ```
6. **View Songs in Playlist Example**

    **Request:**
    ```bash
    GET /music/playlists/1/songs/
    Authorization: Bearer <your_token>


    ```

    **Response:**
    ```json
    [
    {
        "song_id": 5,
        "title": "Relaxing Song",
        "artist": "Artist Name"
    }
    ]


    ```
7. **Remove Songs in Playlist Example**

    **Request:**
    ```bash
    DELETE /music/playlists/1/songs/5/remove/
    Authorization: Bearer <your_token>


    ```

    **Response:**
    ```json
    {
        "message": "Song removed from playlist successfully."
    }


    ```
8. **Get CSRF Token**

    **Request:**
    ```bash
    GET /music/get-csrf/

    ```

    **Response:**
    ```json
    {
        "csrfToken": "random_csrf_token"
    }

    ```

---

## Error Codes

| Code  | Explanation                                  |
|-------|----------------------------------------------|
| 0     | Success                                      |
| 1001  | Invalid request                              |
| 1002  | Missing required fields                      |
| 403   | Forbidden (You don't have permission)        |
| 404   | Resource not found                           |
| 500   | Internal Server Error                        |

---

## Considerations for API Design

Here are some key considerations for API design:

1. **Keep it simple and consistent**: Your API should be easy to understand, and uniformity across endpoints helps developers learn the API quickly.

2. **Document all aspects of the API**: Include detailed documentation with inputs, outputs, error codes, and examples. This helps developers integrate your API more smoothly.

3. **Ensure security**: Authenticate and authorize users properly, using mechanisms like CSRF protection, JWT, and appropriate permissions.

4. **Test thoroughly**: Test your API against the contract to avoid issues in production and ensure that changes to the API are backward compatible.



## Known Issues
### Current Issues
* __Auto Fill Styling Issue:__ When the user auto-fills forms like the login page, it causes a styling issue where the form turns white.

### Planned Features
* __Offline Listening:__ Ability for users to download songs and listen offline.
* __Music Recommendations:__ Suggest songs to users based on their location and what others around them are listening to.
