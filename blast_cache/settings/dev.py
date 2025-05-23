import json
import os

from unipath import Path

from .base import *

DEV_SECRETS_PATH = SETTINGS_PATH.child("dev_secrets.json")
with open(os.path.join(DEV_SECRETS_PATH)) as f: secrets = json.loads(f.read())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'blast_cache_db',
        'USER': get_secret("USER", secrets),
        'PASSWORD': get_secret("PASSWORD", secrets),
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {'TEMPLATE': 'hstemplate'},
    }
}

SECRET_KEY = get_secret("SECRET_KEY", secrets)

DEBUG = True

INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)

# TODO: Change this for staging and production
MEDIA_URL = '/submissions/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'submissions')

USER_CHK = BASE_DIR+"/files/P04591.chk"
USER_PSSM = BASE_DIR+"/files/P04591.pssm"
