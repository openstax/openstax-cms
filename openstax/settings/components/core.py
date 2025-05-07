"""
Core Django settings for OpenStax CMS.

This module contains the fundamental Django settings that are common across all environments.
"""

import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Default to a key starting with django-insecure for local development.
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-wq21wtjo3@d_qfjvd-#td!%7gfy2updj2z+nev^k$iy%=m4_tr')

# Determine if we're in debug mode
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Set allowed hosts based on environment
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
    if ENVIRONMENT == 'prod':
        # Prod only
        ALLOWED_HOSTS = ['openstax.org']
    else:
        # All non-local and non-prod environments - allow all subdomains of openstax.org
        ALLOWED_HOSTS = [".openstax.org"]

# These should both be set to true. The openstax.middleware will handle resolving the URL
# without a redirect if needed.
APPEND_SLASH = True
WAGTAIL_APPEND_SLASH = True

# urls.W002 warns about slashes at the start of URLs. But we need those so
# we don't have to have slashes at the end of URLs. So ignore.
SILENCED_SYSTEM_CHECKS = ['urls.W002']

# Admin configuration
ADMINS = ('Michael Volo', 'volo@rice.edu')

# Default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
SITE_ID = 1

# URL configuration
ROOT_URLCONF = 'openstax.urls'
WSGI_APPLICATION = 'openstax.wsgi.application'

# Base URL configuration
BASE_URL = os.getenv('BASE_URL')
if BASE_URL is None:
    APPLICATION_DOMAIN = os.getenv('APPLICATION_DOMAIN')
    if APPLICATION_DOMAIN is None:
        if ENVIRONMENT == 'prod':
            APPLICATION_DOMAIN = 'openstax.org'
        elif ENVIRONMENT == 'test':
            APPLICATION_DOMAIN = 'dev.openstax.org'
        elif ENVIRONMENT == 'local':
            APPLICATION_DOMAIN = 'dev.openstax.org'
        else:
            APPLICATION_DOMAIN = f'{ENVIRONMENT}.openstax.org'
    BASE_URL = f'https://{APPLICATION_DOMAIN}'

# Server host (used to populate links in the email)
HOST_LINK = os.getenv('HOST_LINK', BASE_URL)
if DEBUG:
    HOST_LINK = 'http://localhost:8000' 