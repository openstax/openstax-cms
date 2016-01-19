from .base import *

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# BASE_URL required for notification emails
BASE_URL = 'http://localhost:8000'

try:
    from .local import *
except ImportError:
    pass


##################################
#        ACCOUNTS SETTINGS       #
##################################

# Use default login, logout and profile urls
APP_LOGIN_URL = None
APP_LOGOUT_URL = None
APP_PROFILE_URL = None

ACCOUNTS_LOGIN_URL = 'https://accounts-qa.openstax.org/login?'
AUTHORIZATION_URL = 'https://accounts-qa.openstax.org/oauth/authorize'
ACCESS_TOKEN_URL = 'https://accounts-qa.openstax.org/oauth/token'
USER_QUERY = 'https://accounts-qa.openstax.org/api/user?'

SOCIAL_AUTH_OPENSTAX_KEY = '0a3c6b8c21091873805181b4b2a42cdbabeec6f6871332b817f59fac37033537'
SOCIAL_AUTH_OPENSTAX_SECRET = '40035a7f2a7948b33ffce370af3918d692b958a6cc195e8b57b1fbe621a88157'

