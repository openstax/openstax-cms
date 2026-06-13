"""Tests for our override of wagtail-transfer's Import (choose) page."""
from django.contrib.auth import get_user_model
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
        self.assertContains(response, 'Select the source environment')
        self.assertContains(response, 'refresh-from-prod-runbook.md')
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
