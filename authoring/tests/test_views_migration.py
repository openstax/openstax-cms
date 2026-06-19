# authoring/tests/test_views_migration.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from wagtail.models import Page
from pages import models as page_models

DEFAULT_LAYOUT = [{"type": "default", "value": {}}]


class MigrationViewTestBase(TestCase):
    """Shared fixtures for migration endpoint tests.

    Provides:
      self.home   — RootPage added to the Wagtail tree root
      self.staff  — superuser staff user (username "migrator")
      self.client — APIClient force-authenticated as self.staff
    """

    def setUp(self):
        root = Page.objects.get(depth=1)
        self.home = page_models.RootPage(title="Home", slug="site-root")
        root.add_child(instance=self.home)
        self.staff = get_user_model().objects.create_user(
            username="migrator", password="x", is_staff=True, is_superuser=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff)


class ExportEndpointTests(MigrationViewTestBase):
    def setUp(self):
        super().setUp()
        self.page = page_models.FlexPage(
            title="Sample", slug="sample", layout=DEFAULT_LAYOUT, body=[],
        )
        self.home.add_child(instance=self.page)

    def test_requires_auth(self):
        anon = APIClient()
        resp = anon.get(f"/apps/cms/api/v2/pages/flex/{self.page.id}/export/")
        self.assertIn(resp.status_code, (401, 403))

    def test_exports_import_shaped_payload(self):
        resp = self.client.get(f"/apps/cms/api/v2/pages/flex/{self.page.id}/export/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(set(data), {"title", "slug", "layout", "body"})
        self.assertEqual(data["slug"], "sample")

    def test_staff_without_edit_permission_forbidden(self):
        plain_staff = get_user_model().objects.create_user(
            username="plain-staff", password="x", is_staff=True,
        )
        client = APIClient()
        client.force_authenticate(user=plain_staff)
        resp = client.get(f"/apps/cms/api/v2/pages/flex/{self.page.id}/export/")
        self.assertEqual(resp.status_code, 403)

    def test_unknown_page_404(self):
        resp = self.client.get("/apps/cms/api/v2/pages/flex/999999/export/")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("errors", resp.json())


class ImportEndpointTests(MigrationViewTestBase):
    def _body(self, **over):
        payload = {
            "parent_id": self.home.id,
            "title": "Imported",
            "slug": "imported",
            "layout": DEFAULT_LAYOUT,
            "body": [],
        }
        payload.update(over)
        return payload

    def test_imports_as_unpublished_draft(self):
        resp = self.client.post(
            "/apps/cms/api/v2/pages/flex/import/", self._body(), format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertFalse(resp.json()["live"])
        self.assertIn("edit_url", resp.json())

    def test_unknown_parent_400(self):
        resp = self.client.post(
            "/apps/cms/api/v2/pages/flex/import/",
            self._body(parent_id=999999), format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_unknown_block_type_400(self):
        resp = self.client.post(
            "/apps/cms/api/v2/pages/flex/import/",
            self._body(body=[{"type": "not_a_block", "value": "x"}]), format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_unauthenticated_rejected(self):
        anon = APIClient()
        resp = anon.post("/apps/cms/api/v2/pages/flex/import/", self._body(), format="json")
        self.assertIn(resp.status_code, (401, 403))

    def test_non_integer_parent_400(self):
        resp = self.client.post(
            "/apps/cms/api/v2/pages/flex/import/",
            self._body(parent_id="abc"), format="json",
        )
        self.assertEqual(resp.status_code, 400)


class CreateEndpointParentIdTests(MigrationViewTestBase):
    """Strict create endpoint (POST /apps/cms/api/v2/pages/flex/) parent_id edge cases."""

    def _body(self, **over):
        payload = {
            "parent_id": self.home.id,
            "title": "X",
            "slug": "x",
            "layout": DEFAULT_LAYOUT,
            "body": [],
        }
        payload.update(over)
        return payload

    def test_non_integer_parent_400(self):
        resp = self.client.post(
            "/apps/cms/api/v2/pages/flex/",
            self._body(parent_id="abc"), format="json",
        )
        self.assertEqual(resp.status_code, 400)
