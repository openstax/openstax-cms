from django.test import TestCase
from django.urls import reverse
from wagtail.test.utils import WagtailTestUtils


class HeadlessUserbarTests(TestCase, WagtailTestUtils):
    """The headless front-end fetches the Wagtail userbar from this endpoint so
    that live-preview scroll restoration, the accessibility/content checker,
    content metrics, and wagtail-ai's content checks work on the decoupled
    front-end (Wagtail headless docs; see ai_assist/README.md)."""

    def test_userbar_renders_for_admin_user(self):
        self.login()  # WagtailTestUtils: create + log in a superuser
        response = self.client.get(reverse('wagtail_userbar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'wagtail-userbar')

    def test_userbar_not_exposed_to_anonymous(self):
        response = self.client.get(reverse('wagtail_userbar'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'wagtail-userbar')

    def test_userbar_response_is_never_cached(self):
        # The body varies by user (admin bar vs empty), so a CDN must never
        # cache it: a cached blank would be served to editors, and a cached
        # admin bar (with edit links) would leak to the anonymous public.
        self.login()
        response = self.client.get(reverse('wagtail_userbar'))
        self.assertIn('no-store', response.headers.get('Cache-Control', ''))
        self.assertIn('Cookie', response.headers.get('Vary', ''))
