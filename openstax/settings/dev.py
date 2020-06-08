from .base import *

DEBUG = True
ALLOWED_HOSTS = ['.openstax.org']

# Allows you to test sending mail, output is logged to the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable Python Social Auth Warnings
LOGGING_CONFIG = None

# Cloudfront static file settings
DEFAULT_FILE_STORAGE = 'storages.S3Storage.S3Storage'
AWS_STORAGE_BUCKET_NAME = 'openstax-assets'
AWS_STORAGE_DIR = 'oscms-dev'
AWS_S3_CUSTOM_DOMAIN = 'd3bxy9euw4e147.cloudfront.net'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=0',
}
# S3 static file storage using custom backend
STATICFILES_LOCATION = '{}/static'.format(AWS_STORAGE_DIR)
STATICFILES_STORAGE = 'openstax.custom_storages.StaticStorage'
#STATIC_URL = "https://%s/%s/static/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STORAGE_DIR)

# S3 media storage using custom backend
MEDIAFILES_LOCATION = '{}/media'.format(AWS_STORAGE_DIR)
MEDIA_URL = "https://%s/%s/media/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STORAGE_DIR)
DEFAULT_FILE_STORAGE = 'openstax.custom_storages.MediaStorage'

# Openstax Accounts
ACCOUNTS_URL = 'https://accounts-dev.openstax.org'
AUTHORIZATION_URL = 'https://accounts-dev.openstax.org/oauth/authorize'
ACCESS_TOKEN_URL = 'https://accounts-dev.openstax.org/oauth/token'
USER_QUERY = 'https://accounts-dev.openstax.org/api/user?'
USERS_QUERY = 'https://accounts-dev.openstax.org/api/users?'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'https://oscms-dev.openstax.org'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

# Server host (used to populate links in the email)
HOST_LINK = 'https://oscms-dev.openstax.org'

#CNX URL for viewing book online
CNX_URL = 'https://dev.cnx.org/'

SCOUT_MONITOR = True
SCOUT_NAME = "openstax-cms (dev)"

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
sentry_sdk.init(
    dsn='https://2e1ecafc60684f86b59c654de3032d83:7fbc901dcca04dc4a8220f7cce20fdd9@sentry.cnx.org/11',
    integrations=[DjangoIntegration()]
)

from scout_apm.api import Config
Config.set(revision_sha=os.popen("git rev-parse HEAD").read().strip())

try:
    from .local import *
except ImportError:
    pass

