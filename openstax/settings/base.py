import os
import sys
import logging.config
from django.utils.log import DEFAULT_LOGGING
from dotenv import load_dotenv
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

load_dotenv()

ENVIRONMENT = os.getenv('ENVIRONMENT')
RELEASE_VERSION = os.getenv('RELEASE_VERSION')
DEPLOYMENT_VERSION = os.getenv('DEPLOYMENT_VERSION')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# check if running local dev server - else default to DEBUG=False
if len(sys.argv) > 1:
    DEBUG = (sys.argv[1] == 'runserver')
else:
    DEBUG = False

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    if ENVIRONMENT == 'prod':
        # Prod only
        ALLOWED_HOSTS = ['openstax.org']
    else:
        # All non-local and non-prod environments
        ALLOWED_HOSTS = [f"{ENVIRONMENT}.openstax.org"]

# These should both be set to true. The openstax.middleware will handle resolving the URL
# without a redirect if needed.
APPEND_SLASH = True
WAGTAIL_APPEND_SLASH = True

# urls.W002 warns about slashes at the start of URLs.  But we need those so
#   we don't have to have slashes at the end of URLs.  So ignore.
SILENCED_SYSTEM_CHECKS = ['urls.W002']

ADMINS = ('Michael Volo', 'volo@rice.edu')

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql",
        'NAME': os.getenv('DATABASE_NAME', 'oscms_prodcms'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'postgres'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}

SALESFORCE = {
    'username': os.getenv('SALESFORCE_USERNAME'),
    'password': os.getenv('SALESFORCE_PASSWORD'),
    'security_token': os.getenv('SALESFORCE_SECURITY_TOKEN'),
    'host': os.getenv('SALESFORCE_HOST', 'test')
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Local time zone for this installation.
TIME_ZONE = 'America/Chicago'

# Language code for this installation.
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
WAGTAIL_I18N_ENABLED = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
# Note that with this set to True, Wagtail will fall back on using numeric dates
# in date fields, as opposed to 'friendly' dates like "24 Sep 2013", because
# Python's strptime doesn't support localised month names: https://code.djangoproject.com/ticket/13339
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

DATE_FORMAT = 'j F Y'

# A "public" directory is used so it can be set as the root directory for nginx
# Media (uploaded) files are stored in S3
# Note: used only if media is set to local storage (local config)
MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')

################
# AWS settings #
################
# Amazon SES mail settings
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
# SERVER_EMAIL = os.getenv('SERVER_EMAIL')
# AWS_SES_REGION_NAME = os.getenv('AWS_SES_REGION_NAME')
# AWS_SES_REGION_ENDPOINT = os.getenv('AWS_SES_REGION_ENDPOINT', 'replaceme')

# S3 settings
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_STORAGE_DIR = os.getenv('AWS_STORAGE_DIR', 'oscms-test')
AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
AWS_DEFAULT_ACL = 'public-read'
AWS_HEADERS = {'Access-Control-Allow-Origin': '*'}

# S3 media storage using custom backend
MEDIAFILES_LOCATION = '{}/media'.format(AWS_STORAGE_DIR)
MEDIA_URL = "https://%s/%s/media/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STORAGE_DIR)
DEFAULT_FILE_STORAGE = 'openstax.custom_storages.MediaStorage'

# Use local storage for media and static files in local environment
if DEBUG or ENVIRONMENT == 'test':
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Default to dummy email backend. Configure dev/production/local backend
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# Static files are stored on the server and served by nginx
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')

# URL prefix for static files.
# Example: "http://openstax.org/static/"
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in various locations.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# django-compressor settings
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

# The default secret key is for local use only
# Make this unique, and don't share it with anybody
SECRET_KEY = os.getenv('SECRET_KEY', 'wq21wtjo3@d_qfjvd-#td!%7gfy2updj2z+nev^k$iy%=m4_tr')

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'healthcheck.middleware.HealthCheckMiddleware',  # has to be before CommonMiddleware
    'openstax.middleware.CommonMiddlewareAppendSlashWithoutRedirect',
    'openstax.middleware.CommonMiddlewareOpenGraphRedirect',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

ROOT_URLCONF = 'openstax.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'openstax.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    # contrib
    'compressor',
    'taggit',
    'modelcluster',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'django_crontab',
    'django_filters',
    'storages',
    'django_ses',
    'import_export',
    'rangefilter',
    'reversion',
    'wagtail_modeladmin',
    # custom
    'accounts',
    'api',
    'pages',
    'books',
    'news',
    'allies',
    'snippets',
    'salesforce',
    'mail',
    'global_settings',
    'errata',
    'extraadminfilters',
    'redirects',
    'oxauth',
    'webinars',
    'donations',
    'wagtailimportexport',
    'versions',
    'oxmenus',
    # wagtail
    'wagtail',
    'wagtail.admin',
    'wagtail.documents',
    'wagtail.snippets',
    'wagtail.users',
    'wagtail.images',
    'wagtail.embeds',
    'wagtail.search',
    'wagtail.contrib.redirects',
    'wagtail.contrib.simple_translation',
    'wagtail.locales',
    'wagtail.contrib.forms',
    'wagtail.sites',
    'wagtail.api.v2',
    'wagtail.contrib.settings',
]

########
# Cron #
########

CRONJOBS = [
    ('0 2 * * *', 'django.core.management.call_command', ['delete_resource_downloads']),
    ('0 6 * * *', 'django.core.management.call_command', ['update_resource_downloads']),
    ('0 0 8 * *', 'django.core.management.call_command', ['update_schools_and_mapbox']),
    ('0 9 * * *', 'django.core.management.call_command', ['update_opportunities']),
    ('0 10 * * *', 'django.core.management.call_command', ['update_partners']),
]

if ENVIRONMENT == 'prod':
    CRONJOBS.append(('0 6 1 * *', 'django.core.management.call_command', ['check_redirects']))

CRONTAB_COMMAND_PREFIX = os.getenv('CRONTAB_COMMAND_PREFIX', '')
CRONTAB_COMMAND_SUFFIX = os.getenv('CRONTAB_COMMAND_SUFFIX', '')
CRONTAB_LOCK_JOBS = os.getenv('CRONTAB_LOCK_JOBS') != 'False'

#########################
# Django Rest Framework #
#########################

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

###########
# Logging #
###########

LOGGING_CONFIG = None
LOGLEVEL = os.environ.get('LOGLEVEL', 'error').upper()
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'healthcheck_filter': {
            '()': 'healthcheck.filter.HealthCheckFilter'
        },
    },
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        # disable logs set with null handler
        'null': {
            'class': 'logging.NullHandler',
        },
        # console logs to stderr
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'django.server': {
            **DEFAULT_LOGGING['handlers']['django.server'],
            'filters': ['healthcheck_filter']
        },
    },
    'loggers': {
        # default for all undefined Python modules
        '': {
            'level': 'ERROR',
            'handlers': ['console'],
        },
        # Our application code
        'openstax': {
            'level': LOGLEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        # Default runserver request logging
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    },
})

BASE_URL = os.getenv('BASE_URL')
if BASE_URL is None:
    APPLICATION_DOMAIN = os.getenv('APPLICATION_DOMAIN')
    if APPLICATION_DOMAIN is None:
        if ENVIRONMENT == 'prod':
            APPLICATION_DOMAIN = 'openstax.org'
        elif ENVIRONMENT == 'test':
            APPLICATION_DOMAIN = 'dev.openstax.org'
        else:
            APPLICATION_DOMAIN = f'{ENVIRONMENT}.openstax.org'
    BASE_URL = f'https://{APPLICATION_DOMAIN}'

WAGTAILADMIN_BASE_URL = BASE_URL

CNX_URL = os.getenv('CNX_URL', 'https://staging.cnx.org/')

# Server host (used to populate links in the email)
HOST_LINK = os.getenv('HOST_LINK', BASE_URL)
if DEBUG:
    HOST_LINK = 'http://localhost:8000'

MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN', 'sdk-replaceme')  # should be the sk from mapbox

#####################
# Openstax Accounts #
#####################

ACCOUNTS_URL = os.getenv('ACCOUNTS_DOMAIN', f'{BASE_URL}/accounts')
AUTHORIZATION_URL = os.getenv('ACCOUNTS_AUTHORIZATION_URL', f'{ACCOUNTS_URL}/oauth/authorize')
ACCESS_TOKEN_URL = os.getenv('ACCOUNTS_ACCESS_TOKEN_URL', f'{ACCOUNTS_URL}/oauth/token')
USER_QUERY = os.getenv('ACCOUNTS_USER_QUERY', f'{ACCOUNTS_URL}/api/user?')
USERS_QUERY = os.getenv('ACCOUNTS_USERS_QUERY', f'{ACCOUNTS_URL}/api/users?')
SOCIAL_AUTH_OPENSTAX_KEY = os.getenv('SOCIAL_AUTH_OPENSTAX_KEY')
SOCIAL_AUTH_OPENSTAX_SECRET = os.getenv('SOCIAL_AUTH_OPENSTAX_SECRET')
SOCIAL_AUTH_LOGIN_REDIRECT_URL = os.getenv('SOCIAL_AUTH_LOGIN_REDIRECT_URL', BASE_URL)
SOCIAL_AUTH_SANITIZE_REDIRECTS = os.getenv('SOCIAL_AUTH_SANITIZE_REDIRECTS') == 'True'
# SSO Cookie defaults to local running accounts instance. Change as necessary using .env
SSO_COOKIE_NAME = os.getenv('SSO_COOKIE_NAME', 'oxa')
SIGNATURE_PUBLIC_KEY = os.getenv('SSO_SIGNATURE_PUBLIC_KEY',
                                 "-----BEGIN PUBLIC KEY-----\
                                 MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDjvO/E8lO+ZJ7JMglbJyiF5/Ae\
                                 IIS2NKbIAMLBMPVBQY7mSqo6j/yxdVNKZCzYAMDWc/VvEfXQQJ2ipIUuDvO+SOwz\
                                 MewQ70hC71hC4s3dmOSLnixDJlnsVpcnKPEFXloObk/fcpK2Vw27e+yY+kIFmV2X\
                                 zrvTnmm9UJERp6tVTQIDAQAB\
                                 -----END PUBLIC KEY-----")
ENCRYPTION_PRIVATE_KEY = os.getenv('SSO_ENCRYPTION_PRIVATE_KEY', "c6d9b8683fddce8f2a39ac0565cf18ee")

###########
# Wagtail #
###########

WAGTAIL_SITE_NAME = 'openstax'
WAGTAILAPI_BASE_URL = os.getenv('WAGTAILAPI_BASE_URL', BASE_URL)
# Wagtail API number of results
WAGTAILAPI_LIMIT_MAX = None
WAGTAIL_USAGE_COUNT_ENABLED = False
WAGTAIL_USER_CUSTOM_FIELDS = ['is_staff']
WAGTAIL_GRAVATAR_PROVIDER_URL = '//www.gravatar.com/avatar'

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}

WAGTAIL_CONTENT_LANGUAGES = [
    ('en', "English"),
    ('es', "Spanish"),
]

from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

WAGTAILIMAGES_FORMAT_CONVERSIONS = {
    'webp': 'webp',
    'jpeg': 'webp',
    'jpg': 'webp',
    'png': 'webp',
}
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

##########
# Sentry #
##########

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.4,  # limit the number of errors sent from production - 40%
    send_default_pii=True,  # this will send the user id of admin users only to sentry to help with debugging
    environment=ENVIRONMENT
)

###################
# Local Overrides #
###################

# To override any of the above settings use a local.py file in this directory
# This should always be at the end of the file.
try:
    from .local import *
except ImportError:
    pass
