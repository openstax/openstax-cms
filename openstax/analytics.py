import logging

from django.conf import settings
from posthog import Posthog

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = getattr(settings, 'POSTHOG_API_KEY', '')
        if not api_key:
            return None
        _client = Posthog(
            api_key=api_key,
            host=getattr(settings, 'POSTHOG_HOST', 'https://us.i.posthog.com'),
        )
    return _client


def _get_user_uuid(request):
    """Resolve the user's OpenStax Accounts UUID from the SSO cookie."""
    try:
        from openstax_accounts.functions import get_logged_in_user_uuid
        return get_logged_in_user_uuid(request)
    except Exception:
        return None


def capture(event, properties=None, request=None):
    """
    Capture an analytics event and send it to PostHog.

    Follows the same conventions as OpenStax Accounts (ox_posthog.rb):
    - distinct_id is always the user's Accounts UUID (from SSO cookie)
    - Events use snake_case naming
    - Every event is tagged with source='cms' and environment

    Because Accounts already $set's the full user profile (role,
    faculty_status, school, etc.) on every event it captures, PostHog
    merges person properties automatically by UUID — no need to
    duplicate that here.

    Args:
        event: Event name in snake_case (e.g. 'errata_submitted')
        properties: Dict of event-specific properties
        request: Django request object (used to resolve user UUID)
    """
    client = _get_client()
    if client is None:
        return

    if properties is None:
        properties = {}

    distinct_id = _get_user_uuid(request) if request is not None else None
    if distinct_id is None:
        return

    properties['source'] = 'cms'
    properties['environment'] = getattr(settings, 'ENVIRONMENT', 'unknown')

    try:
        client.capture(
            distinct_id=str(distinct_id),
            event=event,
            properties=properties,
        )
    except Exception:
        logger.exception('Failed to capture PostHog event: %s', event)
