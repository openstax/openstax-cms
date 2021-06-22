from .base import *

DEBUG = True

###########################################
#        OPENSTAX ACCOUNTS SETTINGS       #
###########################################
AUTHORIZATION_URL = 'https://accounts-qa.openstax.org/oauth/authorize'
ACCESS_TOKEN_URL = 'https://accounts-qa.openstax.org/oauth/token'
USER_QUERY = 'https://accounts-qa.openstax.org/api/user?'
USERS_QUERY = 'https://accounts-qa.openstax.org/api/users?'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'http://cms-dev.openstax.org'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

BYPASS_SSO_COOKIE_CHECK = True

#CNX URL for viewing book online
CNX_URL = 'https://staging.cnx.org/'

SCOUT_MONITOR = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test_oscms_prodcms',
        'USER': 'postgres',
        #'HOST': 'localhost',
        'PASSWORD': 'postgres',
        'PORT': 5432,
    }
}

try:
    from .local import *
except ImportError:
    pass

