import re

from django.test import TestCase, Client

from wagtail.contrib.sitemaps.sitemap_generator import Sitemap

from global_settings.views import SlashlessSitemap


class SlashlessSitemapTest(TestCase):
    """ Verify _urls() strips trailing slashes from the entries Wagtail builds
        from each page's get_sitemap_urls(). A stub parent supplies url_info
        dicts so no page tree / database is required.
    """

    def _sitemap_with_locations(self, *locations):
        class StubParent(Sitemap):
            def _urls(self, page, protocol, domain):
                return [{'location': loc, 'lastmod': None} for loc in locations]

        class StubSitemap(SlashlessSitemap, StubParent):
            pass

        return StubSitemap()

    def test_urls_strip_trailing_slash(self):
        sitemap = self._sitemap_with_locations(
            'https://openstax.org/blog/some-post/',
            'https://openstax.org/details/books/biology-2e/',
        )
        locations = [u['location'] for u in sitemap._urls(1, 'https', 'openstax.org')]
        self.assertEqual(locations, [
            'https://openstax.org/blog/some-post',
            'https://openstax.org/details/books/biology-2e',
        ])

    def test_urls_leave_slashless_unchanged(self):
        sitemap = self._sitemap_with_locations('https://openstax.org/blog/some-post')
        locations = [u['location'] for u in sitemap._urls(1, 'https', 'openstax.org')]
        self.assertEqual(locations, ['https://openstax.org/blog/some-post'])


class SitemapViewTest(TestCase):
    def test_sitemap_locs_are_slashless(self):
        response = Client().get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)

        locs = re.findall(r'<loc>(.*?)</loc>', response.content.decode())
        for loc in locs:
            path = re.sub(r'^https?://[^/]+', '', loc)
            self.assertFalse(
                path.endswith('/'),
                f'sitemap <loc> should be slash-less: {loc}',
            )
