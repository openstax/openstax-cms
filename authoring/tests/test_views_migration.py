# authoring/tests/test_views_migration.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from wagtail.models import Page
from pages import models as page_models

DEFAULT_LAYOUT = [{"type": "default", "value": {}}]


class ExportEndpointTests(TestCase):
    def setUp(self):
        root = Page.objects.get(depth=1)
        self.home = page_models.RootPage(title="Home", slug="site-root")
        root.add_child(instance=self.home)
        self.page = page_models.FlexPage(
            title="Sample", slug="sample", layout=DEFAULT_LAYOUT, body=[],
        )
        self.home.add_child(instance=self.page)
        self.staff = get_user_model().objects.create_user(
            username="ed", password="x", is_staff=True,
        )
        self.client = APIClient()

    def test_requires_auth(self):
        resp = self.client.get(f"/apps/cms/api/v2/pages/flex/{self.page.id}/export/")
        self.assertIn(resp.status_code, (401, 403))

    def test_exports_import_shaped_payload(self):
        self.client.force_authenticate(user=self.staff)
        resp = self.client.get(f"/apps/cms/api/v2/pages/flex/{self.page.id}/export/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(set(data), {"title", "slug", "layout", "body"})
        self.assertEqual(data["slug"], "sample")

    def test_unknown_page_404(self):
        self.client.force_authenticate(user=self.staff)
        resp = self.client.get("/apps/cms/api/v2/pages/flex/999999/export/")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("errors", resp.json())
