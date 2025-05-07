"""
Wagtail CMS settings for OpenStax CMS.

This module contains settings specific to Wagtail CMS.
"""

import os

# Wagtail site settings
WAGTAIL_SITE_NAME = 'OpenStax'
WAGTAILADMIN_BASE_URL = os.getenv('BASE_URL', 'https://openstax.org')
WAGTAILAPI_BASE_URL = os.getenv('WAGTAILAPI_BASE_URL', WAGTAILADMIN_BASE_URL)

# Wagtail API settings
WAGTAILAPI_LIMIT_MAX = None
WAGTAIL_USAGE_COUNT_ENABLED = False
WAGTAIL_GRAVATAR_PROVIDER_URL = '//www.gravatar.com/avatar'

# Wagtail document settings
WAGTAILADMIN_EXTERNAL_LINK_CONVERSION = 'exact'
WAGTAIL_REDIRECTS_FILE_STORAGE = 'cache'
WAGTAILFORMS_HELP_TEXT_ALLOW_HTML = True

# Disable the workflow, we don't use them
WAGTAIL_WORKFLOW_ENABLED = False

# Wagtail search settings
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}

# Wagtail image settings
WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp", "svg"]
WAGTAILIMAGES_FORMAT_CONVERSIONS = {
    'webp': 'webp',
    'jpeg': 'webp',
    'jpg': 'webp',
    'png': 'webp',
}
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

# Wagtail rich text editor settings
WAGTAILADMIN_RICH_TEXT_EDITORS = {
    'default': {
        'WIDGET': 'wagtail.admin.rich_text.DraftailRichTextArea',
        'OPTIONS': {
            'features': ['h1',
                         'h2',
                         'h3',
                         'h4',
                         'h5',
                         'h6',
                         'bold',
                         'italic',
                         'ol',
                         'ul',
                         'hr',
                         'link',
                         'document-link',
                         'image',
                         'embed',
                         'code',
                         'blockquote',
                         'superscript',
                         'subscript',
                         'strikethrough']
        }
    },
}

# Wagtail embed settings
from wagtail.embeds.oembed_providers import youtube, vimeo
WAGTAILEMBEDS_FINDERS = [
    {
        'class': 'wagtail.embeds.finders.oembed',
        'providers': [youtube, vimeo]
    }
] 