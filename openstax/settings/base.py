# Django settings for openstax project.

import os
import raven
import logging.config
from django.utils.log import DEFAULT_LOGGING

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
BASE_DIR = PROJECT_ROOT

DEBUG = True

ADMINS = (
    ('Michael Harrison', 'mwharrison@rice.edu'),
)

# Default to dummy email backend. Configure dev/production/local backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'openstax',
    }
}

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
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'accounts.backend.OpenStax',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.create_user',
    'accounts.pipelines.save_profile',
    'accounts.pipelines.update_email',
    'accounts.pipelines.update_role',
    'accounts.pipelines.update_accounts_profile',
    'accounts.pipelines.update_faculty_status',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)

IMPORT_USER_PIPELINE = (
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.create_user',
    'accounts.pipelines.save_profile',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.user.user_details',
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
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
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
    'admin_view_permission',
    'django.contrib.admin',
    # contrib
    'compressor',
    'taggit',
    'modelcluster',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'raven.contrib.django.raven_compat',
    'django_filters',
    #'social.apps.django_app.default',
    'social_django',
    'storages',
    'django_ses',
    'cachalot',
    # custom
    'admin_templates',  # this overrides the admin templates
    'pages',
    'books',
    'news',
    'allies',
    'accounts',
    'snippets',
    'salesforce',
    'mail',
    'global_settings',
    'errata',
    'extraadminfilters',
    'redirects',
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

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse'
#         }
#     },
#     'formatters': {
#         'simple': {
#             'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
#         },
#     },
#     'handlers': {
#         'mail_admins': {
#             'level': 'ERROR',
#             'filters': ['require_debug_false'],
#             'class': 'django.utils.log.AdminEmailHandler'
#         },
#         'file': {
#             'level': 'ERROR',
#             'class': 'logging.FileHandler',
#             'filename': 'server.log',
#             'formatter': 'simple'
#         },
#     },
#     'loggers': {
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#         'accounts.salesforce': {
#             'handlers': ['file'],
#             'level': 'ERROR',
#             'propagate': True,
#             'formatter': 'simple',
#         },
#     },
# }

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
        # console logs to stderr
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        # Add Handler for Sentry for `warning` and above
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        # default for all undefined Python modules
        '': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry'],
        },
        # Our application code
        'openstax': {
            'level': LOGLEVEL,
            'handlers': ['console', 'sentry'],
            # Avoid double logging because of root logger
            'propagate': False,
        },
        # Prevent noisy modules from logging to Sentry
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console'],
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
# this is what sends tracebacks to Sentry
RAVEN_CONFIG = {
    'dsn': 'https://2e1ecafc60684f86b59c654de3032d83:7fbc901dcca04dc4a8220f7cce20fdd9@sentry.cnx.org/11',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}


# WAGTAIL SETTINGS
WAGTAIL_SITE_NAME = 'openstax'
# Wagtail API number of results
WAGTAILAPI_LIMIT_MAX = None
WAGTAILUSERS_PASSWORD_ENABLED = False

# used in page.models to retrieve book information
CNX_ARCHIVE_URL = 'https://archive.cnx.org'

# Server host (used to populate links in the email)
HOST_LINK = 'https://openstax.org'

WAGTAIL_GRAVATAR_PROVIDER_URL = '//www.gravatar.com/avatar'

try:
    from local import *
except ImportError:
    pass
