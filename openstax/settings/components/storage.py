"""
Storage settings for OpenStax CMS.

Environment Variables:
    AWS_STORAGE_BUCKET_NAME: S3 bucket name for asset storage
    AWS_STORAGE_DIR: Directory within the bucket
    AWS_S3_CUSTOM_DOMAIN: Custom domain for S3 assets
"""

import os
from .core import BASE_DIR

# Environment variables
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# AWS settings
# Amazon SES mail settings
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@openstax.org')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'noreply@openstax.org')
AWS_SES_FROM_EMAIL = 'noreply@openstax.org'
AWS_SES_REGION_NAME = os.getenv('AWS_SES_REGION_NAME', 'us-west-2')
AWS_SES_REGION_ENDPOINT = os.getenv('AWS_SES_REGION_ENDPOINT', 'email.us-west-2.amazonaws.com')
# Default to dummy email backend. Configure dev/production/local backend
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# S3 settings
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'openstax-assets')
AWS_STORAGE_DIR = os.getenv('AWS_STORAGE_DIR', 'oscms-test')
AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN', 'assets.openstax.org')
AWS_DEFAULT_ACL = 'public-read'
AWS_HEADERS = {'Access-Control-Allow-Origin': '*'}

# Static and media files
# Use local storage for media and static files in local environment
if DEBUG or ENVIRONMENT == 'test':
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    # S3 media storage using custom backend
    MEDIAFILES_LOCATION = '{}/media'.format(AWS_STORAGE_DIR)
    MEDIA_URL = "https://%s/%s/media/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STORAGE_DIR)
    DEFAULT_FILE_STORAGE = 'openstax.custom_storages.MediaStorage'

# Static files are stored on the server and served by nginx
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MAX_AGE = 604800  # 7 days

# Enhanced WhiteNoise configuration
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ALLOW_ALL_ORIGINS = True
WHITENOISE_INDEX_FILE = True
WHITENOISE_COMPRESS = True
WHITENOISE_MIMETYPES = {
    'application/javascript': 'application/javascript',
    'text/css': 'text/css',
    'image/svg+xml': 'image/svg+xml',
    'application/json': 'application/json',
    'application/xml': 'application/xml',
    'text/xml': 'text/xml',
    'text/plain': 'text/plain',
    'image/png': 'image/png',
    'image/jpeg': 'image/jpeg',
    'image/gif': 'image/gif',
    'image/webp': 'image/webp',
    'image/x-icon': 'image/x-icon',
    'font/woff': 'font/woff',
    'font/woff2': 'font/woff2',
    'font/ttf': 'font/ttf',
    'font/otf': 'font/otf',
    'font/eot': 'font/eot',
}

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

# A "public" directory is used so it can be set as the root directory for nginx
# Media (uploaded) files are stored in S3
# Note: used only if DEFAULT_FILE_STORAGE is set to local storage (local config set by DEBUG)
MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')

# django-compressor settings
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

# Enhanced django-compressor settings for better performance
COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = not DEBUG
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]
COMPRESS_STORAGE = 'compressor.storage.CompressorFileStorage' 