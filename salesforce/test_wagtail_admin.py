"""Tests for the native Wagtail admin wiring of Salesforce data (see
``salesforce/wagtail_hooks.py``)."""
from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from django.test import TestCase, RequestFactory
from django.urls import reverse

from salesforce.models import Partner
from salesforce.wagtail_hooks import PartnerViewSet, PARTNER_READONLY_FIELDS


def _request(method, path, user):
    rf = RequestFactory()
    request = getattr(rf, method)(path)
    request.user = user
    # Wagtail's messages.success() needs a message store on the request.
    setattr(request, "session", {})
    setattr(request, "_messages", FallbackStorage(request))
    return request


class PartnerSyncViewTests(TestCase):
    def setUp(self):
        self.viewset = PartnerViewSet("partners")
        self.superuser = User.objects.create_superuser("admin", "a@openstax.org", "pw")
        self.plain = User.objects.create_user("editor", "e@openstax.org", "pw", is_staff=True)

    def test_sync_denied_without_change_permission(self):
        request = _request("post", "/admin/partners/sync/", self.plain)
        with self.assertRaises(PermissionDenied):
            self.viewset.sync_view(request)

    @patch("salesforce.wagtail_hooks.management.call_command")
    def test_sync_runs_update_partners_command(self, mock_call):
        request = _request("post", "/admin/partners/sync/", self.superuser)
        response = self.viewset.sync_view(request)
        mock_call.assert_called_once_with("update_partners", verbosity=0)
        self.assertEqual(response.status_code, 302)  # redirects back to index

    @patch("salesforce.wagtail_hooks.management.call_command")
    def test_sync_get_shows_confirmation_without_running(self, mock_call):
        request = _request("get", "/admin/partners/sync/", self.superuser)
        response = self.viewset.sync_view(request)
        mock_call.assert_not_called()
        self.assertEqual(response.status_code, 200)


class PartnerAdminViewTests(TestCase):
    def setUp(self):
        self.client.force_login(
            User.objects.create_superuser("admin", "a@openstax.org", "pw")
        )

    def test_index_renders_with_sync_button(self):
        response = self.client.get(reverse("partners:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sync with Salesforce")

    def test_add_is_denied(self):
        # Wagtail catches the view's PermissionDenied and redirects to the admin
        # home with an error message (its standard permission-denied behaviour).
        response = self.client.get(reverse("partners:add"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("wagtailadmin_home"))

    def test_salesforce_fields_are_read_only(self):
        partner = Partner.objects.create(partner_name="Acme", salesforce_id="SF123")
        response = self.client.get(reverse("partners:edit", args=[partner.pk]))
        self.assertEqual(response.status_code, 200)
        # A read-only panel renders the value but no editable input for the field.
        self.assertNotContains(response, 'name="salesforce_id"')

    @patch("wagtail.admin.views.generic.models.log")
    @patch("salesforce.signals.invalidate_cloudfront_caches")
    def test_edit_save_sets_from_admin_site_and_busts_cache(self, mock_invalidate, _mock_log):
        from salesforce.wagtail_hooks import PartnerEditView

        partner = Partner.objects.create(partner_name="Acme", visible_on_website=False)

        class _FakeForm:
            def __init__(self, instance):
                self.instance = instance

            def save(self):
                self.instance.save()
                return self.instance

            def has_changed(self):
                return True

        view = PartnerEditView()
        view.form = _FakeForm(partner)
        view.save_instance()

        # The viewset's edit save flags the instance so the post_save signal
        # invalidates the CloudFront cache, exactly as the old Django admin did.
        self.assertTrue(partner.from_admin_site)
        mock_invalidate.assert_called_with("salesforce/partners")


class ReadonlyFieldConfigTests(TestCase):
    def test_known_salesforce_fields_are_marked_readonly(self):
        # Guard against accidentally making SF-managed fields editable.
        for field in ("salesforce_id", "account_id", "partner_status", "partner_type"):
            self.assertIn(field, PARTNER_READONLY_FIELDS)
