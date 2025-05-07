"""
Production settings for OpenStax CMS.

This module contains settings specific to the production environment.
"""

from .base import *

# Set environment
ENVIRONMENT = 'prod'
DEBUG = False

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email settings
EMAIL_BACKEND = 'django_ses.SESBackend'

# Sentry settings
SENTRY_DSN = os.getenv('SENTRY_DSN') 