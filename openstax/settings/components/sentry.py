"""
Sentry settings for OpenStax CMS.

This module contains settings for Sentry error tracking.
"""

import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Environment variables
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')

# Sentry configuration
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.4,  # limit the number of errors sent from production - 40%
    send_default_pii=True,  # this will send the user id of admin users only to sentry to help with debugging
    environment=ENVIRONMENT
) 