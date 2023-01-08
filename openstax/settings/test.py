from .base import *

DEBUG = True

###########################################
#        OPENSTAX ACCOUNTS SETTINGS       #
###########################################
AUTHORIZATION_URL = 'https://dev.openstax.org/accounts/oauth/authorize'
ACCESS_TOKEN_URL = 'https://dev.openstax.org/accounts/oauth/token'
USER_QUERY = 'https://dev.openstax.org/accounts/api/user?'
USERS_QUERY = 'https://dev.openstax.org/accounts/api/users?'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'http://dev.openstax.org'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

BYPASS_SSO_COOKIE_CHECK = True

#CNX URL for viewing book online
CNX_URL = 'https://staging.cnx.org/'

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

SALESFORCE = {'username': os.getenv('SALESFORCE_USERNAME'), 'password': os.getenv('SALESFORCE_PASSWORD'), 'security_token': os.getenv('SALESFORCE_SECURITY_TOKEN'), 'sandbox': True}

SOCIAL_AUTH_OPENSTAX_KEY = os.getenv('SOCIAL_AUTH_OPENSTAX_KEY')
SOCIAL_AUTH_OPENSTAX_SECRET = os.getenv('SOCIAL_AUTH_OPENSTAX_SECRET')

EVENTBRITE_API_KEY = os.getenv('EVENTBRITE_API_KEY')
EVENTBRITE_API_SECRET = os.getenv('EVENTBRITE_API_SECRET')
EVENTBRITE_API_PRIVATE_TOKEN = os.getenv('EVENTBRITE_API_PRIVATE_TOKEN')
EVENTBRITE_API_PUBLIC_TOKEN = os.getenv('EVENTBRITE_API_PUBLIC_TOKEN')

# use local storage for uploaded (media) files
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# silence whitenoise warnings for CI
import warnings
warnings.filterwarnings("ignore", message="No directory at", module="whitenoise.base" )

try:
    from .local import *
except ImportError:
    pass
