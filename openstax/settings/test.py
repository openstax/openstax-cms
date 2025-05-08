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

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql",
        'NAME': os.getenv('DATABASE_NAME', 'oscms_test'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'postgres'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}

# silence whitenoise warnings for CI
import warnings
warnings.filterwarnings("ignore", message="No directory at", module="whitenoise.base")
