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

# Wagtail AI: never call a real provider in tests. Both config trees are stubbed:
# BACKENDS (legacy llm rich-text path) use EchoBackend; PROVIDERS (any-llm agent +
# embedding path) point at a non-routable sentinel so a future test that resolves
# an agent/embedding client fails loudly instead of making a billable API call.
# CISafetyTests asserts both stay stubbed.
AI_TEST_STUB_PROVIDER = "openstax-test-stub"
WAGTAIL_AI = {
    "BACKENDS": {
        "default": {"CLASS": "wagtail_ai.ai.echo.EchoBackend", "CONFIG": {"MODEL_ID": "echo"}},
        "quality": {"CLASS": "wagtail_ai.ai.echo.EchoBackend", "CONFIG": {"MODEL_ID": "echo"}},
        "openai": {"CLASS": "wagtail_ai.ai.echo.EchoBackend", "CONFIG": {"MODEL_ID": "echo"}},
    },
    "IMAGE_DESCRIPTION_BACKEND": "default",
    "IMAGE_DESCRIPTION_PROVIDER": "image_description",
    "PROVIDERS": {
        "default": {"provider": AI_TEST_STUB_PROVIDER, "model": "stub"},
        "image_description": {"provider": AI_TEST_STUB_PROVIDER, "model": "stub"},
        "content_feedback": {"provider": AI_TEST_STUB_PROVIDER, "model": "stub"},
        "embedding": {"provider": AI_TEST_STUB_PROVIDER, "model": "stub"},
    },
}
