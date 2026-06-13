"""Tests for the hardened wagtail-transfer export API.

Covers openstax/wagtail_transfer_security.py + wagtail_transfer_urls.py:
the placeholder-key request guard and the exportable-model allowlist.
"""
import hashlib
import hmac

from django.test import TestCase, override_settings
from django.urls import reverse
from wagtail.models import Page


def _digest(key, message):
    return hmac.new(key.encode(), message.encode(), hashlib.sha1).hexdigest()


@override_settings(WAGTAILTRANSFER_SECRET_KEY='unit-test-secret')
class ExportApiSecurityTests(TestCase):
    def _models_url(self, model_path):
        return reverse('wagtail_transfer_model', args=[model_path])

    @override_settings(ENVIRONMENT='staging', WAGTAILTRANSFER_SECRET_KEY='change-me-in-production')
    def test_placeholder_key_blocks_export_on_deployed_env(self):
        page_id = Page.objects.first().id
        url = reverse('wagtail_transfer_pages', args=[page_id])
        resp = self.client.get(url, {'digest': _digest('change-me-in-production', str(page_id))})
        self.assertEqual(resp.status_code, 403)

    def test_auth_user_is_not_exportable(self):
        # Secure key on a deployed env: the insecure-key guard passes, so the
        # allowlist is what must reject auth.user.
        with override_settings(ENVIRONMENT='staging'):
            url = self._models_url('auth.user')
            resp = self.client.get(url, {'digest': _digest('unit-test-secret', 'auth.user')})
        self.assertEqual(resp.status_code, 404)

    def test_allowed_snippet_model_passes_the_guards(self):
        # snippets.subject is in WAGTAILTRANSFER_LOOKUP_FIELDS → allowlisted.
        with override_settings(ENVIRONMENT='staging'):
            url = self._models_url('snippets.subject')
            resp = self.client.get(url, {'digest': _digest('unit-test-secret', 'snippets.subject')})
        # Reaches the real view (which 200s with an empty object list) rather
        # than being rejected by the allowlist/guard.
        self.assertEqual(resp.status_code, 200)

    def test_bad_digest_still_rejected_for_allowed_model(self):
        with override_settings(ENVIRONMENT='staging'):
            url = self._models_url('snippets.subject')
            resp = self.client.get(url, {'digest': 'not-a-valid-digest'})
        self.assertEqual(resp.status_code, 403)
