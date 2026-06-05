from .base import *

DEBUG = True
ENVIRONMENT = 'test'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

SALESFORCE = {
    'username': 'sf@openstax.org',
    'password': 'supersecret',
    'security_token': 'supersecret',
    'host': 'test',
}

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql",
        'NAME': os.getenv('DATABASE_NAME', 'oscms_test'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'postgres'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}

# silence whitenoise warnings for CI
import warnings
warnings.filterwarnings("ignore", message="No directory at", module="whitenoise.base")

# Wagtail AI: never call a real provider in tests; always echo.
WAGTAIL_AI = {
    "BACKENDS": {
        "default": {"CLASS": "wagtail_ai.ai.echo.EchoBackend", "CONFIG": {"MODEL_ID": "echo"}},
        "quality": {"CLASS": "wagtail_ai.ai.echo.EchoBackend", "CONFIG": {"MODEL_ID": "echo"}},
        "openai": {"CLASS": "wagtail_ai.ai.echo.EchoBackend", "CONFIG": {"MODEL_ID": "echo"}},
    },
    "IMAGE_DESCRIPTION_BACKEND": "default",
    "PROVIDERS": {
        "default": {"provider": "anthropic", "model": "claude-3-5-sonnet-latest"},
        "embedding": {"provider": "openai", "model": "text-embedding-3-small"},
    },
}
