"""Tests for our override of wagtail-transfer's Import (choose) page."""
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse


class WagtailTransferChoosePageTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser(
            username='transfer-admin', email='cms@openstax.org', password='secret',
        )
        self.client.force_login(user)

    def test_import_page_uses_override_with_directions(self):
        response = self.client.get(reverse('wagtail_transfer_admin:choose_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtail_transfer/choose_page.html')
        # Our how-to panel
        self.assertContains(response, 'Importing content from another environment')
        self.assertContains(response, 'Pick the source environment')
        self.assertContains(response, 'refresh-from-prod-runbook.md')
        # The Scribe walkthrough link
        self.assertContains(response, 'scribehow.com/o/jGUaNi72Qay710Vi452_JA')
        # The CMS support Slack channel link
        self.assertContains(response, 'openstax.slack.com/archives/C69BU01RC')
        # The draft-vs-published / what-gets-imported details
        self.assertContains(response, 'What actually gets imported')
        self.assertContains(response, 'Draft edits never transfer')
        self.assertContains(response, 'Published state carries over')
        # The updating-vs-replacing details, and the switchover dance within it
        self.assertContains(response, 'Updating a page vs. replacing one at a different URL')
        self.assertContains(response, 'updates it in place')
        self.assertContains(response, 'Promote to home page')
        # The import form component from the original template must survive the override
        self.assertContains(response, 'data-wagtail-component="content-import-form"')

    def test_import_menu_item_shown_without_sources_configured(self):
        """Our menu override shows Import for permitted staff even when no
        WAGTAILTRANSFER_SOURCES are configured (the package hides it otherwise)."""
        from global_settings.wagtail_hooks import WagtailTransferImportMenuItem

        with override_settings(WAGTAILTRANSFER_SOURCES={}):
            item = WagtailTransferImportMenuItem(
                'Import', reverse('wagtail_transfer_admin:choose_page'),
                name='wagtail-transfer-import',
            )
            request = RequestFactory().get('/admin/')
            request.user = get_user_model().objects.get(username='transfer-admin')
            self.assertTrue(item.is_shown(request))


@override_settings(WAGTAILTRANSFER_SOURCES={
    'staging': {'BASE_URL': 'https://staging.example.com/admin/wagtail-transfer/', 'SECRET_KEY': 'shared-secret'},
})
class DoImportErrorHandlingTests(TestCase):
    """A failed import must surface as a Wagtail admin message on the Choose
    page, not an unhandled 500 (openstax.wagtail_transfer_patches, patch 3)."""

    def setUp(self):
        user = get_user_model().objects.create_superuser(
            username='transfer-admin', email='cms@openstax.org', password='secret',
        )
        self.client.force_login(user)

    def test_import_failure_redirects_with_a_readable_message(self):
        # The source returning an HTML error page (403/404/SPA shell) is the
        # realistic failure mode this guards — see AddJsonGuardTests.
        forbidden_response = mock.Mock(content=b'<html><title>403 Forbidden</title></html>')
        with mock.patch('wagtail_transfer.views.requests.get', return_value=forbidden_response):
            response = self.client.post(reverse('wagtail_transfer_admin:import'), {
                'type': 'page',
                'source': 'staging',
                'source_page_id': '1',
                'dest_page_id': '',
            })

        self.assertRedirects(response, reverse('wagtail_transfer_admin:choose_page'))
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(
            any('403 Forbidden' in m for m in messages),
            msg=f'Expected the source response to surface in a message; got {messages}',
        )

    def test_unexpected_exception_also_redirects_with_a_message(self):
        # A non-HTTP failure (network error, bug in wagtail-transfer) must not
        # 500 either — the broad except Exception fallback in the patch.
        with mock.patch('wagtail_transfer.views.requests.get', side_effect=RuntimeError('boom')):
            response = self.client.post(reverse('wagtail_transfer_admin:import'), {
                'type': 'page',
                'source': 'staging',
                'source_page_id': '1',
                'dest_page_id': '',
            })

        self.assertRedirects(response, reverse('wagtail_transfer_admin:choose_page'))
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(any('failed unexpectedly' in m for m in messages), msg=messages)
