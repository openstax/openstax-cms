"""System checks for cross-cutting configuration.

Registered from GlobalSettingsConfig.ready() so settings/base.py stays
declarative. This is the conventional Django home for check registration.
"""
from django.conf import settings
from django.core import checks


@checks.register(checks.Tags.security)
def _check_wagtail_transfer_secret_key(app_configs, **kwargs):
    """Flag a deployed environment still running with the placeholder secret.

    This fires on `manage.py check`/`migrate`/`runserver`. It does NOT run when
    a WSGI/ASGI worker boots the app, and `collectstatic` (the AMI bake step)
    skips it — so it is only one of two guards. The request-time guard in
    openstax.wagtail_transfer_security covers the served process.
    """
    insecure = getattr(settings, 'WAGTAILTRANSFER_INSECURE_SECRET_KEY', 'change-me-in-production')
    if (
        getattr(settings, 'ENVIRONMENT', 'local') not in ('local', 'test')
        and getattr(settings, 'WAGTAILTRANSFER_SECRET_KEY', insecure) == insecure
    ):
        return [checks.Error(
            "WAGTAILTRANSFER_SECRET_KEY is set to the insecure default placeholder.",
            hint="Set the WAGTAILTRANSFER_SECRET_KEY environment variable to a unique secure value.",
            id='openstax.E001',
        )]
    return []
