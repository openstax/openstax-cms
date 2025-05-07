"""
Cron job settings for OpenStax CMS.

This module contains settings for scheduled tasks using django-crontab.
"""

import os

# Environment variables
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')

# Cron jobs
CRONJOBS = [
    # ('0 2 * * *', 'django.core.management.call_command', ['delete_resource_downloads']),
    ('0 6 * * *', 'django.core.management.call_command', ['update_resource_downloads']),
    ('0 0 8 * *', 'django.core.management.call_command', ['update_schools_and_mapbox']),
    ('0 10 * * *', 'django.core.management.call_command', ['update_partners']),
    ('0 11 * * *', 'django.core.management.call_command', ['sync_thank_you_notes']),
]

# Add production-specific cron jobs
if ENVIRONMENT == 'prod':
    CRONJOBS.append(('0 6 1 * *', 'django.core.management.call_command', ['check_redirects']))
    CRONJOBS.append(('0 0 * * *', 'django.core.management.call_command', ['update_opportunities']))

# Cron job configuration
CRONTAB_COMMAND_PREFIX = os.getenv('CRONTAB_COMMAND_PREFIX', '')
CRONTAB_COMMAND_SUFFIX = os.getenv('CRONTAB_COMMAND_SUFFIX', '')
CRONTAB_LOCK_JOBS = os.getenv('CRONTAB_LOCK_JOBS') != 'False' 