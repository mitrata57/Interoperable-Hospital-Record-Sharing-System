
"""
TUTH's settings -- same Django app code as Bir, but pointed at a
different database ENGINE entirely (MariaDB via XAMPP, MySQL-compatible).
This file is never used by default -- only when a server process is
explicitly started with DJANGO_SETTINGS_MODULE=ihrs.settings_tuth,
so Bir's normal `python manage.py runserver` is completely unaffected.
"""

# $env:DJANGO_SETTINGS_MODULE="ihrs.settings_tuth"
import pymysql , os
pymysql.install_as_MySQLdb()  # MUST run before Django touches the DB backend

from .settings import * 

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv('My-DB'),
        "USER": os.getenv('My_USER'),
        "PASSWORD": os.getenv('My_PASSWORD'),  
        "HOST": os.getenv('My_HOST'),   
        "PORT": os.getenv('My-DB_PORT'),
    }
}


