## How to Set Up the Site

When you initially run `python3 manage.py runserver` and you navigate to `http://127.0.0.1:8000/app`, you might receive an error that looks like:

`OperationalError at /app
no such table: app_user
Request Method:	GET
Request URL:	http://127.0.0.1:8000/app
Django Version:	5.0.7
Exception Type:	OperationalError
Exception Value:	
no such table: app_user
Exception Location:	/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/django/db/backends/sqlite3/base.py, line 329, in execute
Raised during:	app.views.user_list
Python Executable:	/Library/Frameworks/Python.framework/Versions/3.10/bin/python3
Python Version:	3.10.7
Python Path:	
['/Users/sebastianskontos/Desktop/Uni/Year 3/Semester '
 '2/ELEC3609/Lab-03-Group-01/mysite',
 '/Library/Frameworks/Python.framework/Versions/3.10/lib/python310.zip',
 '/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10',
 '/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/lib-dynload',
 '/Users/sebastianskontos/Library/Python/3.10/lib/python/site-packages',
 '/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages']
Server time:	Mon, 16 Sep 2024 23:54:40 +0000`

The reason for this is that the database hasn't been setup within Django's framework. To do this, run the command `python3 manage.py makemigrations app` and then run the command `python3 manage.py migrate`.