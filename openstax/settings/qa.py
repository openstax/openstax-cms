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
STATIC_URL = "https://%s/%s/static/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STORAGE_DIR)
# S3 media storage using custom backend
MEDIAFILES_LOCATION = '{}/media'.format(AWS_STORAGE_DIR)
MEDIA_URL = "https://%s/%s/media/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STORAGE_DIR)
DEFAULT_FILE_STORAGE = 'openstax.custom_storages.MediaStorage'

# Openstax Accounts
AUTHORIZATION_URL = 'https://accounts-qa.openstax.org/oauth/authorize'
ACCESS_TOKEN_URL = 'https://accounts-qa.openstax.org/oauth/token'
USER_QUERY = 'https://accounts-qa.openstax.org/api/user?'
USERS_QUERY = 'https://accounts-qa.openstax.org/api/users?'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'https://oscms-qa.openstax.org'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False
OPENSTAX_ACCOUNTS_LOGOUT_URL = 'https://accounts-qa.openstax.org/signout'

# Server host (used to populate links in the email)
HOST_LINK = 'https://oscms-qa.openstax.org'

try:
    from .local import *
except ImportError:
    pass
