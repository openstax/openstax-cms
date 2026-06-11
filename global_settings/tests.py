import json
import re

from django.test import TestCase, Client
from django.utils import timezone

from wagtail.contrib.sitemaps.sitemap_generator import Sitemap

from wagtail.models import Page, Site

from global_settings.views import SlashlessSitemap
from news.models import NewsIndex, NewsArticle
from pages.models import HomePage


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

    def test_urls_leave_missing_locations_unchanged(self):
        sitemap = self._sitemap_with_locations(None, 'https://openstax.org/blog/some-post/')
        locations = [u['location'] for u in sitemap._urls(1, 'https', 'openstax.org')]
        self.assertEqual(locations, [None, 'https://openstax.org/blog/some-post'])


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


class RobotsViewTest(TestCase):
    """ /robots.txt serves the static baseline rules plus a Disallow entry for
        every page that was published and later unpublished (CORE-2256), so
        crawlers stop indexing pages editors have pulled down. Never-published
        drafts are deliberately left out — listing them would leak their slugs.
    """

    @classmethod
    def setUpTestData(cls):
        root_page = Page.objects.get(title="Root")
        homepage = HomePage(title="Hello World", slug="hello-world")
        root_page.add_child(instance=homepage)
        # Point the default site at the homepage so get_url_parts() can
        # resolve site-relative paths for the article pages.
        Site.objects.update_or_create(
            is_default_site=True,
            defaults={'hostname': 'testserver', 'port': 80, 'root_page': homepage},
        )
        cls.news_index = NewsIndex(title="News Index")
        homepage.add_child(instance=cls.news_index)

    def _robots(self):
        response = Client().get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        return response.content.decode()

    def _add_article(self, slug):
        article = NewsArticle(
            title=slug,
            slug=slug,
            date=timezone.now(),
            heading='Heading',
            subheading='Subheading',
            author='OpenStax',
            body=json.dumps([{'type': 'paragraph', 'value': '<p>Body</p>'}]),
            live=False,
        )
        self.news_index.add_child(instance=article)
        return article

    def test_serves_baseline_rules(self):
        content = self._robots()
        self.assertIn('User-agent: *', content)
        self.assertIn('Disallow: /errata', content)
        self.assertIn('User-agent: GPTBot', content)
        self.assertIn('Sitemap: http://testserver/sitemap.xml', content)

    def test_unpublished_blog_post_is_disallowed(self):
        article = self._add_article('robots-unpublished-post')
        article.save_revision().publish()
        article.refresh_from_db()
        article.unpublish()
        self.assertIn('Disallow: /blog/robots-unpublished-post', self._robots())

    def test_live_blog_post_is_not_disallowed(self):
        article = self._add_article('robots-live-post')
        article.save_revision().publish()
        self.assertNotIn('robots-live-post', self._robots())

    def test_never_published_draft_is_not_disallowed(self):
        self._add_article('robots-draft-post')
        self.assertNotIn('robots-draft-post', self._robots())
