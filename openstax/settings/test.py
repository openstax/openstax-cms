from .base import *

DEBUG = True

###########################################
#        OPENSTAX ACCOUNTS SETTINGS       #
###########################################
AUTHORIZATION_URL = 'https://accounts-dev.openstax.org/oauth/authorize'
ACCESS_TOKEN_URL = 'https://accounts-dev.openstax.org/oauth/token'
USER_QUERY = 'https://accounts-dev.openstax.org/api/user?'
USERS_QUERY = 'https://accounts-dev.openstax.org/api/users?'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'http://cms-dev.openstax.org'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

BYPASS_SSO_COOKIE_CHECK = True

#CNX URL for viewing book online
CNX_URL = 'https://staging.cnx.org/'

SCOUT_MONITOR = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'localhost',
        'PASSWORD': 'postgres',
        'PORT': 5432,
    }
}

SALESFORCE = {'username': os.getenv('SALESFORCE_USERNAME'), 'password': os.getenv('SALESFORCE_PWD'), 'security_token': os.getenv('SALESFORCE_TOKEN'), 'sandbox': True}

SOCIAL_AUTH_OPENSTAX_KEY = os.getenv('SOCIAL_AUTH_OPENSTAX_KEY')
SOCIAL_AUTH_OPENSTAX_SECRET = os.getenv('SOCIAL_AUTH_OPENSTAX_SECRET')

EVENTBRITE_API_KEY = os.getenv('EVENTBRITE_API_KEY')
EVENTBRITE_API_SECRET = os.getenv('EVENTBRITE_API_SECRET')
EVENTBRITE_API_PRIVATE_TOKEN = os.getenv('EVENTBRITE_API_PRIVATE_TOKEN')
EVENTBRITE_API_PUBLIC_TOKEN = os.getenv('EVENTBRITE_API_PUBLIC_TOKEN')


try:
    from .local import *
except ImportError:
    pass

