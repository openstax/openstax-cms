# authoring/tests/test_drafts.py
from django.test import TestCase
from wagtail.models import Page
from pages import models as page_models
from authoring.routing_rules import validate_page_location, RoutingError
from django.contrib.auth import get_user_model
from authoring.permissions import CanDraftFlexPages

DEFAULT_LAYOUT = [{"type": "default", "value": {}}]
LANDING_LAYOUT = [{"type": "landing", "value": {"nav_links": [], "show_give_now_button": True}}]


class RoutingRulesTests(TestCase):
    def setUp(self):
        root = Page.objects.get(depth=1)
        self.home = page_models.RootPage(title="Home", slug="site-root")
        root.add_child(instance=self.home)

    def test_unique_slug_returned_unchanged(self):
        slug, warnings = validate_page_location(self.home, "fresh-slug")
        self.assertEqual(slug, "fresh-slug")
        self.assertEqual(warnings, [])

    def test_tree_global_collision_gets_suffixed_with_warning(self):
        existing = page_models.FlexPage(title="Existing", slug="dup", layout=DEFAULT_LAYOUT, body=[])
        self.home.add_child(instance=existing)
        slug, warnings = validate_page_location(self.home, "dup")
        self.assertEqual(slug, "dup-1")
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["code"], "slug_collision")
        self.assertEqual(warnings[0]["existing_page_id"], existing.id)

    def test_reserved_slug_raises(self):
        with self.assertRaises(RoutingError):
            validate_page_location(self.home, "books")

    def test_reserved_slug_is_case_insensitive(self):
        with self.assertRaises(RoutingError):
            validate_page_location(self.home, "Books")

    def test_non_rootpage_parent_raises(self):
        portal = page_models.FlexPage(title="Portal", slug="portal", layout=LANDING_LAYOUT, body=[])
        self.home.add_child(instance=portal)
        with self.assertRaises(RoutingError):
            validate_page_location(portal, "child")


class PermissionTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.perm = CanDraftFlexPages()

    def _req(self, user):
        class R:  # minimal stand-in for a DRF request
            pass
        r = R()
        r.user = user
        return r

    def test_anonymous_denied(self):
        from django.contrib.auth.models import AnonymousUser
        self.assertFalse(self.perm.has_permission(self._req(AnonymousUser()), None))

    def test_non_staff_denied(self):
        u = self.User.objects.create_user("editor", password="x", is_staff=False)
        self.assertFalse(self.perm.has_permission(self._req(u), None))

    def test_staff_allowed(self):
        u = self.User.objects.create_user("staff", password="x", is_staff=True)
        self.assertTrue(self.perm.has_permission(self._req(u), None))


from authoring.drafts import (
    validate_layout, validate_body, FlexValidationError,
)


class LayoutValidationTests(TestCase):
    def test_missing_layout_is_error(self):
        with self.assertRaises(FlexValidationError):
            validate_layout([])

    def test_unknown_layout_type_is_error(self):
        with self.assertRaises(FlexValidationError):
            validate_layout([{"type": "fancy", "value": {}}])

    def test_default_layout_ok(self):
        cleaned = validate_layout([{"type": "default", "value": {}}])
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0].block_type, "default")


class BodyValidationTests(TestCase):
    def test_valid_html_block_passes(self):
        cleaned = validate_body([
            {"type": "html", "value": "<p>Hello students</p>"},
        ])
        self.assertEqual(cleaned[0].block_type, "html")

    def test_unknown_block_type_is_error(self):
        with self.assertRaises(FlexValidationError) as ctx:
            validate_body([{"type": "not_a_block", "value": {}}])
        self.assertIn("not_a_block", str(ctx.exception))


from authoring.drafts import create_flex_draft


class CreateDraftTests(TestCase):
    def setUp(self):
        root = Page.objects.get(depth=1)
        self.home = page_models.RootPage(title="Home", slug="site-root")
        root.add_child(instance=self.home)

    def test_create_makes_unpublished_draft(self):
        page, warnings = create_flex_draft(
            parent=self.home,
            title="Why OpenStax",
            slug="why-openstax",
            layout_data=[{"type": "default", "value": {}}],
            body_data=[{"type": "html", "value": "<p>Great for students</p>"}],
        )
        page.refresh_from_db()
        self.assertFalse(page.live)                       # never auto-published
        self.assertTrue(page.has_unpublished_changes)
        self.assertIsNotNone(page.get_latest_revision())  # draft revision exists
        self.assertEqual(page.slug, "why-openstax")


from authoring.drafts import update_flex_draft


class UpdateDraftTests(TestCase):
    def setUp(self):
        root = Page.objects.get(depth=1)
        self.home = page_models.RootPage(title="Home", slug="site-root")
        root.add_child(instance=self.home)
        self.page = page_models.FlexPage(
            title="Live Title", slug="live-page",
            layout=[{"type": "default", "value": {}}],
            body=[{"type": "html", "value": "<p>original</p>"}],
        )
        self.home.add_child(instance=self.page)
        self.page.save_revision().publish()   # make a real live version
        self.page.refresh_from_db()
        self.assertTrue(self.page.live)

    def test_update_creates_draft_without_changing_live(self):
        update_flex_draft(
            page=self.page,
            title="Draft Title",
            layout_data=[{"type": "landing", "value": {"nav_links": [], "show_give_now_button": True}}],
            body_data=[{"type": "html", "value": "<p>changed</p>"}],
        )
        live = page_models.FlexPage.objects.get(id=self.page.id)
        self.assertEqual(live.title, "Live Title")               # live untouched
        self.assertIn("original", str(live.body))                # live body untouched
        self.assertTrue(live.has_unpublished_changes)
        latest = live.get_latest_revision_as_object()
        self.assertEqual(latest.title, "Draft Title")            # draft has the change
        self.assertIn("changed", str(latest.body))


from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


class FlexDraftEndpointTests(TestCase):
    def setUp(self):
        root = Page.objects.get(depth=1)
        self.home = page_models.RootPage(title="Home", slug="site-root")
        root.add_child(instance=self.home)
        self.User = get_user_model()
        self.staff = self.User.objects.create_user("staff", password="x", is_staff=True, is_superuser=True)
        self.token = Token.objects.create(user=self.staff)
        self.client = APIClient()

    def _auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_requires_auth(self):
        resp = self.client.post("/apps/cms/api/v2/pages/flex/", {}, format="json")
        self.assertIn(resp.status_code, (401, 403))

    def test_create_returns_201_and_review_urls(self):
        self._auth()
        resp = self.client.post("/apps/cms/api/v2/pages/flex/", {
            "parent_id": self.home.id,
            "title": "Why OpenStax",
            "slug": "why-openstax",
            "layout": [{"type": "default", "value": {}}],
            "body": [{"type": "html", "value": "<p>Great for students</p>"}],
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        data = resp.json()
        self.assertFalse(data["live"])
        self.assertIn("/admin/pages/", data["edit_url"])
        self.assertTrue(data["preview_url"])
        self.assertEqual(data["warnings"], [])

    def test_invalid_body_returns_400_with_correctable_errors(self):
        self._auth()
        resp = self.client.post("/apps/cms/api/v2/pages/flex/", {
            "parent_id": self.home.id,
            "title": "Bad",
            "slug": "bad",
            "layout": [{"type": "default", "value": {}}],
            "body": [{"type": "not_a_block", "value": {}}],
        }, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("body", resp.json()["errors"])

    def test_slug_collision_creates_with_suffix_and_warns(self):
        self._auth()
        existing = page_models.FlexPage(title="Dup", slug="dup",
                                        layout=[{"type": "default", "value": {}}], body=[])
        self.home.add_child(instance=existing)
        resp = self.client.post("/apps/cms/api/v2/pages/flex/", {
            "parent_id": self.home.id, "title": "Dup2", "slug": "dup",
            "layout": [{"type": "default", "value": {}}], "body": [],
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        data = resp.json()
        self.assertEqual(data["slug"], "dup-1")
        self.assertEqual(data["warnings"][0]["code"], "slug_collision")

    def test_patch_updates_existing_draft(self):
        self._auth()
        page, _ = create_flex_draft(
            parent=self.home, title="Orig", slug="patch-me",
            layout_data=[{"type": "default", "value": {}}],
            body_data=[{"type": "html", "value": "<p>orig</p>"}],
        )
        resp = self.client.patch(f"/apps/cms/api/v2/pages/flex/{page.id}/", {
            "title": "Patched",
            "body": [{"type": "html", "value": "<p>new</p>"}],
        }, format="json")
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["id"], page.id)
        self.assertFalse(resp.json()["live"])  # update never publishes

    def test_reserved_slug_rejected_at_endpoint(self):
        self._auth()
        resp = self.client.post("/apps/cms/api/v2/pages/flex/", {
            "parent_id": self.home.id, "title": "Books", "slug": "books",
            "layout": [{"type": "default", "value": {}}], "body": [],
        }, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("slug", resp.json()["errors"])

    def test_authenticated_non_staff_denied(self):
        nonstaff = self.User.objects.create_user("editor2", password="x", is_staff=False)
        token = Token.objects.create(user=nonstaff)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        resp = self.client.post("/apps/cms/api/v2/pages/flex/", {
            "parent_id": self.home.id, "title": "X", "slug": "x",
            "layout": [{"type": "default", "value": {}}], "body": [],
        }, format="json")
        self.assertEqual(resp.status_code, 403)


from authoring.drafts import validate_rich_text_references
from wagtail.images import get_image_model


class RichTextReferenceTests(TestCase):
    def setUp(self):
        root = Page.objects.get(depth=1)
        self.home = page_models.RootPage(title="Home", slug="site-root")
        root.add_child(instance=self.home)

    def _section_with_html(self, html):
        return [{"type": "section", "value": {
            "content": [{"type": "text", "value": html}], "config": []}}]

    def test_valid_page_link_passes(self):
        body = self._section_with_html(f'<p><a linktype="page" id="{self.home.id}">home</a></p>')
        validate_rich_text_references(body)  # should not raise

    def test_unknown_page_link_raises(self):
        body = self._section_with_html('<p><a linktype="page" id="999999">ghost</a></p>')
        with self.assertRaises(FlexValidationError) as ctx:
            validate_rich_text_references(body)
        self.assertIn("references", ctx.exception.errors)
        self.assertEqual(ctx.exception.errors["references"]["missing"]["page"], [999999])

    def test_unknown_image_embed_raises(self):
        body = self._section_with_html('<p><embed embedtype="image" id="888888" alt="x" format="left"/></p>')
        with self.assertRaises(FlexValidationError):
            validate_rich_text_references(body)

    def test_valid_image_embed_passes(self):
        ImageModel = get_image_model()
        from wagtail.images.tests.utils import get_test_image_file
        img = ImageModel.objects.create(title="Test img", file=get_test_image_file())
        body = self._section_with_html(f'<p><embed embedtype="image" id="{img.id}" alt="x" format="left"/></p>')
        validate_rich_text_references(body)  # should not raise

    def test_no_refs_passes(self):
        body = self._section_with_html('<p>Just plain text, no refs.</p>')
        validate_rich_text_references(body)  # should not raise


class PageLockEndpointTests(TestCase):
    def setUp(self):
        root = Page.objects.get(depth=1)
        self.home = page_models.RootPage(title="Home", slug="site-root")
        root.add_child(instance=self.home)
        self.User = get_user_model()
        self.staff = self.User.objects.create_user("staff_lock", password="x", is_staff=True, is_superuser=True)
        self.token = Token.objects.create(user=self.staff)
        self.client = APIClient()

    def _auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_create_with_stale_page_ref_returns_400(self):
        self._auth()
        resp = self.client.post("/apps/cms/api/v2/pages/flex/", {
            "parent_id": self.home.id, "title": "Ref", "slug": "ref-test",
            "layout": [{"type": "default", "value": {}}],
            "body": [{"type": "section", "value": {
                "content": [{"type": "text", "value": '<p><a linktype="page" id="999999">x</a></p>'}],
                "config": []}}],
        }, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("references", resp.json()["errors"])

    def test_patch_locked_page_returns_409(self):
        self._auth()
        page, _ = create_flex_draft(
            parent=self.home, title="Lockme", slug="lock-me",
            layout_data=[{"type": "default", "value": {}}], body_data=[],
        )
        page.locked = True
        page.save()
        resp = self.client.patch(f"/apps/cms/api/v2/pages/flex/{page.id}/", {
            "title": "Nope",
        }, format="json")
        self.assertEqual(resp.status_code, 409)


from wagtail.images.tests.utils import Image, get_test_image_file


class ImageSearchTests(TestCase):
    def test_search_filters_by_title_and_returns_id(self):
        Image.objects.create(title="Calculus diagram", file=get_test_image_file())
        Image.objects.create(title="History map", file=get_test_image_file())
        resp = self.client.get("/apps/cms/api/v2/images/?search=Calculus")
        self.assertEqual(resp.status_code, 200)
        items = resp.json()["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Calculus diagram")
        self.assertIn("id", items[0])
        # download_url is exposed under "meta" by OpenStaxImagesAPIViewSet
        # (existing public API shape — the agent reads it from there).
        self.assertIn("download_url", items[0]["meta"])
