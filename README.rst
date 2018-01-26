================================
AURA Steering: Program Scheduler
================================

Installation
============

To get setup you must have the following installed:

 * MySQL-Client Development libraries
 * JPEG library development files
 * Python 3.5 including Development files
 * virtualenv 1.11

In Debian or Ubuntu (or derivatives) you should be able to achieve this with this command:

    $ sudo apt-get install libmysqlclient-dev libjpeg-dev python3.5-dev virtualenv


Setting up the environment
--------------------------

Create a virtual environment where the dependencies will live:

    $ virtualenv -p python3.5 python
    $ source python/bin/activate
    (python)$

Change into the base directory of this software and install the project dependencies:

    (python)$ pip3 install -r requirements.txt


Setting up the database
-----------------------

By default the project is set up to run on a SQLite database.

Create a file pv/local_settings.py and add at least the line

    SECRET_KEY = 'secret key'

(obviously replacing "secret key" with a key of your choice).

Then run:

    (python)$ python manage.py migrate
    (python)$ python manage.py loaddata program/fixtures/*.yaml

### Setting up MySQL

__Note:__ When adding your database, make sure you _don't_ use the collation _utf8mb4_unicode_ci_ or you will get a key length error during migration. (use e.g. _utf8_general_ci_ instead).

To use MySQL, add the following to your local_settings.py (before migrating):

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {
                'read_default_file': os.path.join(PROJECT_DIR, 'mysql.cnf'),
            },
        }
    }

Create a file pv/mysql.cnf and give your MySQL credentials:

    [client]
    database =
    host = localhost
    port = 3309
    user =
    password =
    default-character-set = utf8


Adding an admin user
--------------------

In order to create an admin user (which you will need to login to the webinterface after the next step) run:

    (python)$ python manage.py createsuperuser


Running a web server
--------------------

In development you should run:

    (python)$ python manage.py runserver

After this you can open http://127.0.0.1:8000/admin in your browser and log in with the admin credential you created previously.