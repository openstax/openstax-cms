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


import uuid as uuid_module
from datetime import timedelta
from unittest.mock import patch

from botocore.exceptions import ClientError, NoCredentialsError
from django.utils import timezone
from wagtail.models import Site
from wagtail.signals import page_published

from global_settings.functions import (
    PAGE_PUBLISH_PATHS,
    flush_pending_page_invalidation,
    invalidate_cloudfront_caches,
    request_page_invalidation,
)
from global_settings.models import CloudfrontDistribution


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
