from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-lgqlx9bsd#$$tdfpxb#(bk!2s38_ay!)^8m@&jfqu3f%#j2+-e'

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'snap_db',
        'USER': 'user_snap',
        'PASSWORD': '72Nobife!',
        'HOST': 'localhost',
        'PORT': '',
    }
}

STATIC_URL = 'static/'

STATICFILES_DIRS = [
]