from .base import *

DEBUG = True
ENVIRONMENT = 'test'

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

SALESFORCE = {
    'username': 'sf@openstax.org',
    'password': 'supersecret',
    'security_token': 'supersecret',
    'host': 'test',
}

# silence whitenoise warnings for CI
import warnings
warnings.filterwarnings("ignore", message="No directory at", module="whitenoise.base")
