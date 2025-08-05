from .base import *

# If local.py is present, any settings in it will override those in base.py and dev.py.
# Use this for any settings that are specific to this one installation, such as developer API keys.
# local.py should not be checked in to version control.

EMBEDLY_KEY = 'get-one-from-http://embed.ly/'
# GOOGLE_MAPS_KEY = 'get-one-from-https://code.google.com/apis/console/?noredirect'

# It is strongly recommended that you define a SECRET_KEY here, where it won't be visible
# in your version control system.
SECRET_KEY = 'enter-a-long-unguessable-string-here'


# When developing Wagtail templates, we recommend django-debug-toolbar
# for keeping track of page rendering times. To use it:
#     pip install django-debug-toolbar==1.0.1
# and uncomment the lines below.

# from .base import INSTALLED_APPS, MIDDLEWARE_CLASSES
# INSTALLED_APPS += (
#     'debug_toolbar',
# )
# MIDDLEWARE_CLASSES += (
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# )
# # django-debug-toolbar settings
# DEBUG_TOOLBAR_CONFIG = {
#     'INTERCEPT_REDIRECTS': False,
# }
INSTALLED_APPS += (
    'corsheaders',
)
MIDDLEWARE += (
    'corsheaders.middleware.CorsMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql",
        'NAME': 'openstax',
        'USER': 'postgres',
        'HOST': 'postgres',
        'PASSWORD': 'password',
        'PORT': 5432,
    }
}

SALESFORCE = { 'username' : '',
               'password' : '', # password might need to be concatinated with security_token e.g. 'mypass1231'
               'security_token' : '',
               'sandbox': True }

MAPBOX_TOKEN = '' # should be the sk from mapbox

#################
#  Media        #
#################
# locally, we want to use local storage for uploaded (media) files
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

#################
#  CORS         #
#################
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000' # http://localhost:3000, not http://localhost:3000/
]

# As of Django 1.10, we need to be explicit with localhost being allowed
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']
