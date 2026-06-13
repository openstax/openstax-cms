"""Server-side PostHog capture.

Fire-and-forget. A hard no-op unless ``settings.POSTHOG_API_KEY`` is set, so
local development and CI are unaffected. Never lets analytics break a request.
"""
import logging
import uuid

from django.conf import settings
from posthog import Posthog

logger = logging.getLogger(__name__)

_client = None
_client_key = None


def _get_client():
    global _client, _client_key
    key = getattr(settings, 'POSTHOG_API_KEY', None)
    if not key:
        return None
    if _client is None or _client_key != key:
        _client = Posthog(
            key,
            host=getattr(settings, 'POSTHOG_HOST', 'https://z.openstax.org'),
        )
        _client_key = key
    return _client


def capture(event, distinct_id=None, properties=None):
    """Capture a server-side event.

    ``distinct_id`` should be the accounts UUID when known, so the event joins
    the visitor's existing PostHog identity (and the Salesforce pipeline).
    When unknown, the event is sent anonymously with no person profile.
    """
    client = _get_client()
    if client is None:
        return

    props = dict(properties or {})
    props.setdefault('source', 'server')

    if distinct_id:
        did = str(distinct_id)
    else:
        did = str(uuid.uuid4())
        props['$process_person_profile'] = False

    try:
        client.capture(distinct_id=did, event=event, properties=props)
    except Exception:  # noqa: BLE001 — analytics must never break a request
        logger.exception('PostHog capture failed for event %s', event)
