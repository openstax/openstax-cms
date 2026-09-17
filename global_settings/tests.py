import json
import re
import uuid as uuid_module
from datetime import timedelta
from unittest.mock import patch

from botocore.exceptions import ClientError, NoCredentialsError
from django.test import TestCase, Client, RequestFactory
from django.utils import timezone
from wagtail.contrib.sitemaps.sitemap_generator import Sitemap
from wagtail.models import Page, Site
from wagtail.signals import page_published

from global_settings.functions import (
    PAGE_PUBLISH_PATHS,
    flush_pending_page_invalidation,
    invalidate_cloudfront_caches,
    request_page_invalidation,
)
from global_settings.models import CloudfrontDistribution, Footer
from global_settings.views import FrontendOnlyPagesSitemap, SlashlessSitemap, sitemap
from openstax.frontend_routes import (
    FORM_PAGE_ROUTES, SLUG_MISMATCHES, STATIC_PAGES, sitemap_routes,
)
from pages.models import FlexPage, FormHeadings, RootPage


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



class FooterSocialLinksApiTest(TestCase):
    """social_links is additive: the three legacy *_link fields keep serving an
    old, currently-deployed frontend untouched, while social_links carries the
    full ordered list (including platforms, like Instagram/YouTube, that never
    had a dedicated field)."""

    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        self.footer = Footer.for_site(site)
        self.footer.facebook_link = 'https://facebook.com/openstax'
        self.footer.twitter_link = 'https://twitter.com/openstax'
        self.footer.linkedin_link = 'https://linkedin.com/company/openstax'
        self.footer.social_links = json.dumps([
            {'type': 'social_link', 'value': {'platform': 'facebook', 'url': 'https://facebook.com/openstax'}},
            {'type': 'social_link', 'value': {'platform': 'twitter', 'url': 'https://twitter.com/openstax'}},
            {'type': 'social_link', 'value': {'platform': 'linkedin', 'url': 'https://linkedin.com/company/openstax'}},
            {'type': 'social_link', 'value': {'platform': 'instagram', 'url': 'https://www.instagram.com/openstax/'}},
            {'type': 'social_link', 'value': {'platform': 'youtube', 'url': 'https://www.youtube.com/openstax/'}},
        ])
        self.footer.save()

    def test_social_links_present_in_order(self):
        response = self.client.get('/apps/cms/api/footer/')
        data = response.json()
        self.assertEqual(
            [link['platform'] for link in data['social_links']],
            ['facebook', 'twitter', 'linkedin', 'instagram', 'youtube'],
        )
        self.assertEqual(data['social_links'][3]['url'], 'https://www.instagram.com/openstax/')
        self.assertEqual(data['social_links'][4]['url'], 'https://www.youtube.com/openstax/')

    def test_legacy_link_fields_still_present(self):
        response = self.client.get('/apps/cms/api/footer/')
        data = response.json()
        self.assertEqual(data['facebook_link'], 'https://facebook.com/openstax')
        self.assertEqual(data['twitter_link'], 'https://twitter.com/openstax')
        self.assertEqual(data['linkedin_link'], 'https://linkedin.com/company/openstax')


class WagtailTransferChooserCssHookTest(TestCase):
    """The wagtail-transfer chooser renders its pagination arrows as
    <svg class="icon ... navigate-pages">, relying on a global `.icon` size
    that Wagtail 7.4 dropped. We inject a scoped stylesheet via the
    insert_global_admin_css hook (loaded on every admin page, including the
    chooser) to size them back down."""

    def test_global_admin_css_links_the_transfer_chooser_stylesheet(self):
        from wagtail import hooks

        outputs = ''.join(str(fn()) for fn in hooks.get_hooks('insert_global_admin_css'))

        self.assertIn('<link', outputs)
        self.assertIn('wagtail_transfer_chooser', outputs)


def _make_distribution():
    return CloudfrontDistribution.objects.create(
        site=Site.objects.first(), distribution_id='DISTID123')


def _client_error():
    return ClientError({'Error': {'Code': 'Boom', 'Message': 'boom'}}, 'CreateInvalidation')


class InvalidateCloudfrontCachesTests(TestCase):
    def setUp(self):
        self.distribution = _make_distribution()
        patcher = patch('global_settings.functions.boto3.client')
        self.boto_client = patcher.start()
        self.addCleanup(patcher.stop)
        self.create_invalidation = self.boto_client.return_value.create_invalidation

    def _batch(self, call_index=0):
        return self.create_invalidation.call_args_list[call_index].kwargs['InvalidationBatch']

    def test_no_distribution_is_noop(self):
        CloudfrontDistribution.objects.all().delete()
        self.assertFalse(invalidate_cloudfront_caches('footer'))
        self.create_invalidation.assert_not_called()

    def test_single_path_string(self):
        self.assertTrue(invalidate_cloudfront_caches('footer'))
        batch = self._batch()
        self.assertEqual(batch['Paths']['Items'], ['/apps/cms/api/footer*'])
        self.assertEqual(batch['Paths']['Quantity'], 1)

    def test_path_list_batched_into_one_call(self):
        self.assertTrue(invalidate_cloudfront_caches(PAGE_PUBLISH_PATHS))
        self.create_invalidation.assert_called_once()
        batch = self._batch()
        self.assertEqual(batch['Paths']['Quantity'], len(PAGE_PUBLISH_PATHS))
        self.assertIn('/apps/cms/api/v2/pages*', batch['Paths']['Items'])
        self.assertIn('/apps/cms/api/books/resources*', batch['Paths']['Items'])

    def test_no_path_wipes_whole_api(self):
        self.assertTrue(invalidate_cloudfront_caches())
        self.assertEqual(self._batch()['Paths']['Items'], ['/apps/cms/api/*'])

    def test_caller_reference_unique_per_call(self):
        invalidate_cloudfront_caches('footer')
        invalidate_cloudfront_caches('footer')
        refs = [self._batch(i)['CallerReference'] for i in range(2)]
        self.assertNotEqual(refs[0], refs[1])
        for ref in refs:
            uuid_module.UUID(ref)  # raises if not a real uuid

    def test_client_error_is_logged_not_raised(self):
        self.create_invalidation.side_effect = _client_error()
        with self.assertLogs('global_settings.functions', level='ERROR'):
            self.assertFalse(invalidate_cloudfront_caches('footer'))

    def test_missing_credentials_logged_not_raised(self):
        self.create_invalidation.side_effect = NoCredentialsError()
        with self.assertLogs('global_settings.functions', level='WARNING'):
            self.assertFalse(invalidate_cloudfront_caches('footer'))


class PageInvalidationThrottleTests(TestCase):
    def setUp(self):
        self.distribution = _make_distribution()
        patcher = patch('global_settings.functions.boto3.client')
        self.boto_client = patcher.start()
        self.addCleanup(patcher.stop)
        self.create_invalidation = self.boto_client.return_value.create_invalidation

    def _refresh(self):
        self.distribution.refresh_from_db()
        return self.distribution

    def test_first_publish_invalidates_immediately(self):
        request_page_invalidation()
        self.create_invalidation.assert_called_once()
        self.assertFalse(self._refresh().invalidation_pending)
        self.assertIsNotNone(self.distribution.last_invalidated_at)

    def test_publish_within_window_marks_pending(self):
        self.distribution.last_invalidated_at = timezone.now()
        self.distribution.save()
        request_page_invalidation()
        self.create_invalidation.assert_not_called()
        self.assertTrue(self._refresh().invalidation_pending)

    def test_publish_after_window_invalidates_again(self):
        self.distribution.last_invalidated_at = timezone.now() - timedelta(seconds=301)
        self.distribution.save()
        request_page_invalidation()
        self.create_invalidation.assert_called_once()
        self.assertFalse(self._refresh().invalidation_pending)

    def test_flush_sends_pending_invalidation(self):
        self.distribution.invalidation_pending = True
        self.distribution.save()
        flush_pending_page_invalidation()
        self.create_invalidation.assert_called_once()
        self.assertFalse(self._refresh().invalidation_pending)
        self.assertIsNotNone(self.distribution.last_invalidated_at)

    def test_flush_without_pending_is_noop(self):
        flush_pending_page_invalidation()
        self.create_invalidation.assert_not_called()

    def test_blank_distribution_id_is_noop(self):
        self.distribution.distribution_id = ''
        self.distribution.save()
        request_page_invalidation()
        flush_pending_page_invalidation()
        self.create_invalidation.assert_not_called()
        refreshed = self._refresh()
        self.assertFalse(refreshed.invalidation_pending)
        self.assertIsNone(refreshed.last_invalidated_at)

    def test_failed_invalidation_stays_pending_for_retry(self):
        self.create_invalidation.side_effect = _client_error()
        with self.assertLogs('global_settings.functions', level='ERROR'):
            request_page_invalidation()
        self.assertTrue(self._refresh().invalidation_pending)

    def test_page_published_signal_invalidates_page_paths(self):
        page_published.send(sender=None, instance=None)
        self.create_invalidation.assert_called_once()
        items = self.create_invalidation.call_args.kwargs['InvalidationBatch']['Paths']['Items']
        self.assertIn('/apps/cms/api/v2/pages*', items)


class ResourceSnippetInvalidationTests(TestCase):
    def setUp(self):
        self.distribution = _make_distribution()
        patcher = patch('global_settings.functions.boto3.client')
        self.boto_client = patcher.start()
        self.addCleanup(patcher.stop)
        self.create_invalidation = self.boto_client.return_value.create_invalidation

    def test_faculty_resource_save_invalidates_page_paths(self):
        from snippets.models import FacultyResource
        FacultyResource.objects.create(heading='Test Faculty Resource')
        self.create_invalidation.assert_called_once()
        items = self.create_invalidation.call_args.kwargs['InvalidationBatch']['Paths']['Items']
        self.assertIn('/apps/cms/api/v2/pages*', items)
        self.assertIn('/apps/cms/api/books/resources*', items)

    def test_student_resource_save_invalidates_page_paths(self):
        from snippets.models import StudentResource
        StudentResource.objects.create(heading='Test Student Resource')
        self.create_invalidation.assert_called_once()
        items = self.create_invalidation.call_args.kwargs['InvalidationBatch']['Paths']['Items']
        self.assertIn('/apps/cms/api/v2/pages*', items)
        self.assertIn('/apps/cms/api/books/resources*', items)


class FrontendOnlyPagesSitemapTest(TestCase):
    """ Routes osweb serves from the SPA have no Wagtail page, so the page-tree
        sitemap cannot see them -- which is why /adoption was absent from
        sitemap.xml entirely and Google had no way to discover it (CORE-736).

        The section is built from the same registry the OG middleware resolves,
        so the point of these tests is the invariant rather than the list: a
        route advertised here has to answer a crawler, which is the failure
        mode the ticket is about.
    """

    CRAWLER_USER_AGENT = (
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    )

    def _form_headings(self, **overrides):
        """ The single record /adoption and /interest take their copy from. """
        root_page = Page.objects.get(title='Root')
        homepage = RootPage(title='Hello World', slug='openstax-homepage')
        root_page.add_child(instance=homepage)
        fields = dict(
            title='Form Headings',
            slug='form-headings',
            adoption_intro_heading="Let us know you're using OpenStax",
            adoption_intro_description='<p>Tell us you have adopted.</p>',
            interest_intro_heading='Interested in learning more about OpenStax?',
            interest_intro_description='<p>We will send you more information.</p>',
        )
        fields.update(overrides)
        headings = FormHeadings(**fields)
        homepage.add_child(instance=headings)
        return headings

    def _sitemap_paths(self):
        response = Client().get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        return [
            re.sub(r'^https?://[^/]+', '', loc)
            for loc in re.findall(r'<loc>(.*?)</loc>', response.content.decode())
        ]

    def _assert_advertised_routes_resolve(self):
        """ Every SPA-only route sitemap.xml advertises has to answer a crawler.

            This is the whole reason the sitemap and the middleware share one
            registry: /blog was advertised while hard-404ing to crawlers, and
            nothing failed until Search Console noticed. Asserted against the
            paths actually in the XML, not against sitemap_routes(), so the
            check is on the output rather than on the list it came from.
        """
        client = Client(HTTP_USER_AGENT=self.CRAWLER_USER_AGENT)
        candidates = {
            '/{}'.format(route)
            for route in FORM_PAGE_ROUTES + tuple(STATIC_PAGES)
        }
        advertised = [path for path in self._sitemap_paths() if path in candidates]
        # a section that advertised nothing would pass the loop vacuously
        self.assertTrue(advertised)
        for path in advertised:
            self.assertEqual(
                client.get(path).status_code, 200,
                '{} is in sitemap.xml but does not resolve for a crawler'.format(path),
            )

    def test_frontend_only_routes_are_advertised(self):
        self._form_headings()
        paths = self._sitemap_paths()
        for route in FORM_PAGE_ROUTES + tuple(STATIC_PAGES):
            self.assertIn('/{}'.format(route), paths)

    def test_routes_resolved_from_a_cms_page_are_not_duplicated(self):
        """Routes in SLUG_MISMATCHES resolve to a real CMS page, which the
        Wagtail section already covers. Listing them here too would advertise
        the same content under two URLs."""
        self._form_headings()
        for route in SLUG_MISMATCHES:
            self.assertNotIn(route, sitemap_routes())

    def test_form_routes_are_not_advertised_without_their_record(self):
        """The middleware can only build the /adoption and /interest snapshots
        from the FormHeadings record, and falls through to a 404 without it. So
        until that record exists the sitemap must not advertise them, or it
        hands Google exactly the dead URL this registry exists to prevent."""
        paths = self._sitemap_paths()
        for route in FORM_PAGE_ROUTES:
            self.assertNotIn('/{}'.format(route), paths)
        # ...while the routes that don't depend on CMS content stay listed
        for route in STATIC_PAGES:
            self.assertIn('/{}'.format(route), paths)

    def test_form_routes_are_not_advertised_while_their_record_is_a_draft(self):
        """Publication state feeds through the same gate: the middleware only
        renders a live, public FormHeadings record, so a drafted or unpublished
        one has to drop out of the sitemap too rather than advertise a URL that
        404s."""
        headings = self._form_headings()
        headings.live = False
        headings.save()
        paths = self._sitemap_paths()
        for route in FORM_PAGE_ROUTES:
            self.assertNotIn('/{}'.format(route), paths)
        self._assert_advertised_routes_resolve()

    def test_advertised_routes_resolve_for_a_crawler(self):
        self._form_headings()
        self._assert_advertised_routes_resolve()

    def test_advertised_routes_resolve_with_no_form_headings_record(self):
        """Same invariant on a database with nothing backing the form routes:
        the section has to shrink to what still resolves rather than keep
        advertising them."""
        self._assert_advertised_routes_resolve()


class SitemapDocumentTest(TestCase):
    """ Properties of the /sitemap.xml response itself, now that it is built
        from two sections rather than one.
    """

    def setUp(self):
        root_page = Page.objects.get(title='Root')
        site = Site.objects.filter(is_default_site=True).first()
        site.root_page = root_page
        site.save()
        self.homepage = RootPage(title='Hello World', slug='openstax-homepage')
        root_page.add_child(instance=self.homepage)
        self.about = FlexPage(title='About', slug='about')
        self.homepage.add_child(instance=self.about)
        self.headings = FormHeadings(
            title='Form Headings',
            slug='form-headings',
            adoption_intro_heading="Let us know you're using OpenStax",
            adoption_intro_description='<p>Tell us you have adopted.</p>',
            interest_intro_heading='Interested in learning more about OpenStax?',
            interest_intro_description='<p>We will send you more information.</p>',
        )
        self.homepage.add_child(instance=self.headings)
        # what production has: every live page carries a publish date
        Page.objects.all().update(last_published_at=timezone.now())
        self.headings.refresh_from_db()

    def _body(self):
        response = Client().get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_both_sections_render_as_one_urlset(self):
        """A second entry in the sitemaps dict does not turn this into a sitemap
        index. django.contrib.sitemaps.views.sitemap concatenates every
        section's URLs into one <urlset>; views.index is the one that emits an
        index and reverses a per-section URL name, and it isn't routed here. So
        no sitemap-<section>.xml wiring is needed for the new section."""
        body = self._body()
        self.assertIn('<urlset', body)
        self.assertNotIn('<sitemapindex', body)
        # one document carrying URLs from both sections
        self.assertIn('/about</loc>', body)
        self.assertIn('/adopters</loc>', body)

    def test_response_tells_caches_to_revalidate(self):
        """The frontend-only section is derived from CMS state at request time,
        so a cached copy can advertise /adoption after the middleware has
        stopped serving it -- the same inconsistency, moved to the edge. The
        origin says so itself rather than relying on CDN configuration."""
        response = Client().get('/sitemap.xml')
        self.assertEqual(response.headers['Cache-Control'], 'no-cache')

    def test_last_modified_survives_the_second_section(self):
        """views.sitemap only sets Last-Modified when *every* section reports a
        latest_lastmod, so an undated section silently takes the header off the
        whole document -- including the Wagtail section that supplies it in
        production today."""
        with_section = Client().get('/sitemap.xml')
        self.assertIn('Last-Modified', with_section.headers)

        request = RequestFactory().get('/sitemap.xml')
        wagtail_only = sitemap(
            request, sitemaps={'wagtail': SlashlessSitemap(request)})
        self.assertEqual(
            with_section.headers['Last-Modified'],
            wagtail_only.headers['Last-Modified'],
            'the added section changed the document date',
        )

    def test_form_routes_report_their_records_publish_date(self):
        """A crawler learns the copy changed from <lastmod>, and for these
        routes that date is a real one: when the FormHeadings record was last
        published."""
        url_blocks = re.findall(r'<url>(.*?)</url>', self._body(), re.S)
        adoption = [b for b in url_blocks if '/adoption</loc>' in b]
        self.assertEqual(len(adoption), 1)
        self.assertIn(
            self.headings.last_published_at.strftime('%Y-%m-%d'), adoption[0])

    def test_static_routes_get_no_invented_date(self):
        """/adopters copy lives in this repo, not in the CMS, so there is no
        honest date to report for it."""
        url_blocks = re.findall(r'<url>(.*?)</url>', self._body(), re.S)
        adopters = [b for b in url_blocks if '/adopters</loc>' in b]
        self.assertEqual(len(adopters), 1)
        self.assertNotIn('<lastmod>', adopters[0])
