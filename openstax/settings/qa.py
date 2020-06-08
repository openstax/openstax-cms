from .base import *

DEBUG = False
ALLOWED_HOSTS = ['.openstax.org']

# Cloudfront static file settings
DEFAULT_FILE_STORAGE = 'storages.S3Storage.S3Storage'
AWS_STORAGE_BUCKET_NAME = 'openstax-assets'
AWS_STORAGE_DIR = 'oscms-qa'
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
ACCOUNTS_URL = 'https://accounts-qa.openstax.org'
AUTHORIZATION_URL = 'https://accounts-qa.openstax.org/oauth/authorize'
ACCESS_TOKEN_URL = 'https://accounts-qa.openstax.org/oauth/token'
USER_QUERY = 'https://accounts-qa.openstax.org/api/user?'
USERS_QUERY = 'https://accounts-qa.openstax.org/api/users?'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'https://oscms-qa.openstax.org'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

# Server host (used to populate links in the email)
HOST_LINK = 'https://oscms-qa.openstax.org'

#CNX URL for viewing book online
CNX_URL = 'https://qa.cnx.org/'

SCOUT_MONITOR = True
SCOUT_NAME = "openstax-cms (qa)"

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
sentry_sdk.init(
    dsn='https://2e1ecafc60684f86b59c654de3032d83:7fbc901dcca04dc4a8220f7cce20fdd9@sentry.cnx.org/11',
    integrations=[DjangoIntegration()]
)

try:
    from .local import *
except ImportError:
    pass
