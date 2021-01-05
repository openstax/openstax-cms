from .base import *

DEBUG = True

###########################################
#        OPENSTAX ACCOUNTS SETTINGS       #
###########################################
AUTHORIZATION_URL = 'https://accounts-qa.openstax.org/oauth/authorize'
ACCESS_TOKEN_URL = 'https://accounts-qa.openstax.org/oauth/token'
USER_QUERY = 'https://accounts-qa.openstax.org/api/user?'
USERS_QUERY = 'https://accounts-qa.openstax.org/api/users?'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'http://os-webview-dev.openstax.org'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

BYPASS_SSO_COOKIE_CHECK = True

#CNX URL for viewing book online
CNX_URL = 'https://staging.cnx.org/'

try:
    from .local import *
except ImportError:
    pass

