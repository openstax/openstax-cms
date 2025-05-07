"""
Docker settings for OpenStax CMS.

This module contains settings specific to the Docker environment.
"""

from .base import *

# If local.py is present, any settings in it will override those in base.py and dev.py.
# Use this for any settings that are specific to this one installation, such as developer API keys.
# local.py should not be checked in to version control.

# API keys
EMBEDLY_KEY = 'get-one-from-http://embed.ly/'
# GOOGLE_MAPS_KEY = 'get-one-from-https://code.google.com/apis/console/?noredirect'

# Secret key for Docker environment
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

# Add CORS headers
INSTALLED_APPS += (
    'corsheaders',
)
MIDDLEWARE += (
    'corsheaders.middleware.CorsMiddleware',
)

# Database settings for Docker
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

# Salesforce settings for Docker
SALESFORCE = { 
    'username': '',
    'password': '', # password might need to be concatenated with security_token e.g. 'mypass1231'
    'security_token': '',
    'sandbox': True 
}

# Mapbox token for Docker
MAPBOX_TOKEN = '' # should be the sk from mapbox

#################
#  Media        #
#################
# Media settings for Docker
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

#################
#  CORS         #
#################
# CORS settings for Docker
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000' # http://localhost:3000, not http://localhost:3000/
]

# Allow localhost in Docker
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']
