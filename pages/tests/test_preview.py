from unittest.mock import patch

from django.test import TestCase

from pages import models as page_models


class RootPageServePreviewTests(TestCase):
    """serve_preview must not bake the Site record's scheme into the redirect.

    The conventional Site config uses port 80, so get_url_parts() returns an
    http:// site_root. Behind the TLS-terminating proxy the admin is served over
    HTTPS, so an absolute http:// preview URL is blocked as mixed content. The
    redirect must stay root-relative so it inherits the admin's https origin
    (matching the path-relative URL convention in openstax/functions.py).
    """

    @patch('pages.models.RootPage.get_url_parts')
    def test_root_preview_redirect_is_scheme_relative(self, mock_get_url_parts):
        mock_get_url_parts.return_value = (1, 'http://dev.openstax.org', '')
        root_page = page_models.RootPage()
        response = root_page.serve_preview(None, 'some-mode')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.url.startswith('http://'))
        self.assertEqual(response.url, '/?preview=some-mode')

    @patch('pages.models.RootPage.get_url_parts')
    def test_subpage_preview_redirect_is_scheme_relative(self, mock_get_url_parts):
        mock_get_url_parts.return_value = (1, 'http://dev.openstax.org', '/about-us')
        root_page = page_models.RootPage()
        response = root_page.serve_preview(None, 'some-mode')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.url.startswith('http://'))
        self.assertEqual(response.url, '/about-us/?preview=some-mode')

    @patch('pages.models.RootPage.get_url_parts')
    def test_preview_falls_back_when_no_site(self, mock_get_url_parts):
        mock_get_url_parts.return_value = None
        root_page = page_models.RootPage()
        with patch('wagtail.models.Page.serve_preview') as mock_super:
            mock_super.return_value = 'fallback'
            result = root_page.serve_preview(None, 'some-mode')
        self.assertEqual(result, 'fallback')
