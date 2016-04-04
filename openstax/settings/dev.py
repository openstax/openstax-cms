from .base import *

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# BASE_URL required for notification emails
BASE_URL = 'http://localhost:8000'

###########################################
#        OPENSTAX ACCOUNTS SETTINGS       #
###########################################

AUTHORIZATION_URL = 'https://accounts-dev.openstax.org/oauth/authorize'
ACCESS_TOKEN_URL = 'https://accounts-dev.openstax.org/oauth/token'
USER_QUERY = 'https://accounts-dev.openstax.org/api/user?'

SOCIAL_AUTH_OPENSTAX_KEY = '5deb24ba03f289fae3ceba10f21a5c75449db827bb675440c27244413399ab9b'
SOCIAL_AUTH_OPENSTAX_SECRET = '61c881b26f3eac336d2bf5f4f2314a948b6aee2acc396f0a3200074c64af7203'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'http://os-webview-dev.openstax.org'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

# setting log file to dev is causing issues on testing servers.
# LOGGING['handlers']['file']['filename'] = 'dev.log'

# Disable Python Social Auth Warnings
LOGGING['disable_existing_loggers'] = True
try:
    from .local import *
except ImportError:
    pass

