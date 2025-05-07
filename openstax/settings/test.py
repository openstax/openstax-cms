"""
Test settings for OpenStax CMS.

This module contains settings specific to the test environment.
"""

from .base import *

# Set environment
DEBUG = True
ENVIRONMENT = 'test'

# Use local storage for media and static files
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Salesforce settings for testing
SALESFORCE = {
    'username': 'sf@openstax.org',
    'password': 'supersecret',
    'security_token': 'supersecret',
    'host': 'test',
}

# Silence whitenoise warnings for CI
import warnings
warnings.filterwarnings("ignore", message="No directory at", module="whitenoise.base")
