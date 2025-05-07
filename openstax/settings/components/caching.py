"""
Caching settings for OpenStax CMS.

This module contains caching-related settings for the application.
"""

import os
from .core import BASE_DIR

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'PARSER_CLASS': 'redis.connection.HiredisParser',
        'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
        'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            },
        'MAX_CONNECTIONS': 1000,
        'RETRY_ON_TIMEOUT': True,
        'SOCKET_TIMEOUT': 5,
        'SOCKET_CONNECT_TIMEOUT': 5,
        'KEY_PREFIX': 'openstax_cms',
        'TIMEOUT': 60 * 60 * 24,  # 24 hours
    }
}

# Cache middleware settings
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 60 * 60 * 24  # 24 hours
CACHE_MIDDLEWARE_KEY_PREFIX = 'openstax_cms'

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Wagtail cache settings
WAGTAIL_CACHE = True
WAGTAIL_CACHE_BACKEND = 'default'
WAGTAIL_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours

# Template fragment caching
TEMPLATE_FRAGMENT_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours

# Database query caching
DB_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours 