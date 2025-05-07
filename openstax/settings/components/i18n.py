"""
Internationalization settings for OpenStax CMS.

This module contains settings related to internationalization and localization.
"""

# Internationalization settings
TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DATE_FORMAT = 'j F Y'

# Wagtail i18n settings
WAGTAIL_I18N_ENABLED = True

WAGTAIL_CONTENT_LANGUAGES = [
    ('en', "English"),
    ('es', "Spanish"),
] 