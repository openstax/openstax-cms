# Django settings for openstax project.

import os
import sys
import raven
import logging.config
from django.utils.log import DEFAULT_LOGGING

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
BASE_DIR = PROJECT_ROOT

# check if running local dev server - else default to DEBUG=False
if len(sys.argv) > 1:
    DEBUG = (sys.argv[1] == 'runserver')
else:
    DEBUG = False

# These should both be set to true. The openstax.middleware will handle resolving the URL
# without a redirect if needed.
APPEND_SLASH = True
WAGTAIL_APPEND_SLASH=True

# urls.W002 warns about slashes at the start of URLs.  But we need those so
#   we don't have to have slashes at the end of URLs.  So ignore.
SILENCED_SYSTEM_CHECKS = ['urls.W002']

ADMINS = (
    ('Michael Harrison', 'mwharrison@rice.edu'),
)

# Default to dummy email backend. Configure dev/production/local backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'oscms_prodcms',
    }
}

DEFAULT_AUTO_FIELD='django.db.models.AutoField'

# Local time zone for this installation.
TIME_ZONE = 'America/Chicago'

# Language code for this installation.
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
# Note that with this set to True, Wagtail will fall back on using numeric dates
# in date fields, as opposed to 'friendly' dates like "24 Sep 2013", because
# Python's strptime doesn't support localised month names: https://code.djangoproject.com/ticket/13339
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

DATE_FORMAT = 'j F Y'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# ** You would never normally put the SECRET_KEY in a public repository,
# ** however this is a demo app so we're using the default settings.
# ** Don't use this key in any non-demo usage!
# Make this unique, and don't share it with anybody.
SECRET_KEY = 'wq21wtjo3@d_qfjvd-#td!%7gfy2updj2z+nev^k$iy%=m4_tr'

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'openstax.middleware.CommonMiddlewareAppendSlashWithoutRedirect',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'oxauth.backend.OpenStax',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    #'social_core.pipeline.social_auth.social_user',
    'oxauth.pipelines.social_user',
    'social_core.pipeline.user.create_user',
    'oxauth.pipelines.save_profile',
    'oxauth.pipelines.update_email',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

IMPORT_USER_PIPELINE = (
    'social_django.pipeline.social_auth.social_user',
    'social_django.pipeline.user.create_user',
    'oxauth.pipelines.save_profile',
    'social_django.pipeline.social_auth.associate_user',
    'social_django.pipeline.user.user_details',
)
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

ROOT_URLCONF = 'openstax.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'openstax.wsgi.application'

INSTALLED_APPS = [
    'scout_apm.django',
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
    'raven.contrib.django.raven_compat',
    'django_filters',
    'social_django',
    'storages',
    'django_ses',
    'import_export',
    'django_extensions',
    'inline_actions',
    # custom
    'accounts',
    'admin_templates',  # this overrides the admin templates
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
    'rangefilter',
    'reversion',
    'redirects',
    'oxauth',
    'events',
    'webinars',
    'donations',
    # wagtail
    'wagtail.core',
    'wagtail.admin',
    'wagtail.documents',
    'wagtail.snippets',
    'wagtail.users',
    'wagtail.images',
    'wagtail.embeds',
    'wagtail.search',
    'wagtail.contrib.redirects',
    'wagtail.contrib.forms',
    'wagtail.sites',
    #'wagtail.contrib.wagtailapi',
    'wagtail.api.v2',
    'wagtail.contrib.settings',
    'wagtail.contrib.modeladmin',
    'wagtailimportexport',
    'flags',
    'duplicatebooks'

]

EMAIL_SUBJECT_PREFIX = '[openstax] '

INTERNAL_IPS = ('127.0.0.1', '10.0.2.2')

# django-compressor settings
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

#django rest framework settings
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
   'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    # Schools API is timing out, use this to paginate the results
    #'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    #'PAGE_SIZE': 100
}

LOGGING_CONFIG = None
LOGLEVEL = os.environ.get('LOGLEVEL', 'error').upper()
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        #disable logs set with null handler
        'null': {
            'class': 'logging.NullHandler',
        },
        # console logs to stderr
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
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

# FLAGS
FLAGS = {
    'hide_faculty_resources': [],
}


# WAGTAIL SETTINGS
WAGTAIL_SITE_NAME = 'openstax'
# Wagtail API number of results
WAGTAILAPI_LIMIT_MAX = None
WAGTAILUSERS_PASSWORD_ENABLED = False
WAGTAIL_USAGE_COUNT_ENABLED = False
WAGTAIL_USER_CUSTOM_FIELDS = ['is_staff', ]

# used in page.models to retrieve book information
CNX_ARCHIVE_URL = 'https://archive.cnx.org'

# Server host (used to populate links in the email)
HOST_LINK = 'https://openstax.org'

WAGTAIL_GRAVATAR_PROVIDER_URL = '//www.gravatar.com/avatar'

MAPBOX_TOKEN = '' # should be the sk from mapbox, put in the appropriate settings file

# Openstax Accounts
ACCOUNTS_URL = 'https://accounts.openstax.org'
AUTHORIZATION_URL = 'https://accounts.openstax.org/oauth/authorize'
ACCESS_TOKEN_URL = 'https://accounts.openstax.org/oauth/token'
USER_QUERY = 'https://accounts.openstax.org/api/user?'
USERS_QUERY = 'https://accounts.openstax.org/api/users?'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'https://openstax.org'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

SSO_COOKIE_NAME = 'oxa'
BYPASS_SSO_COOKIE_CHECK = False

SIGNATURE_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDjvO/E8lO+ZJ7JMglbJyiF5/Ae\nIIS2NKbIAMLBMPVBQY7mSqo6j/yxdVNKZCzYAMDWc/VvEfXQQJ2ipIUuDvO+SOwz\nMewQ70hC71hC4s3dmOSLnixDJlnsVpcnKPEFXloObk/fcpK2Vw27e+yY+kIFmV2X\nzrvTnmm9UJERp6tVTQIDAQAB\n-----END PUBLIC KEY-----\n"
ENCRYPTION_PRIVATE_KEY = "c6d9b8683fddce8f2a39ac0565cf18ee"
ENCRYPTION_METHOD = 'A256GCM'
SIGNATURE_ALGORITHM = 'RS256'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

STATIC_HOST = 'https://d3bxy9euw4e147.cloudfront.net' if not DEBUG else ''
STATIC_URL = STATIC_HOST + '/static/'

AWS_HEADERS = {
    'Access-Control-Allow-Origin': '*'
}

WAGTAILIMAGES_FORMAT_CONVERSIONS = {
    'webp': 'webp',
}

WAGTAILIMAGES_MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2MB

# to override any of the above settings use a local.py file in this directory
try:
    from .local import *
except ImportError:
    pass
