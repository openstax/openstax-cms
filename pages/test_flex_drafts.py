# pages/test_flex_drafts.py
from django.test import TestCase
from wagtail.models import Page
from pages import models as page_models
from pages.routing_rules import validate_page_location, RoutingError
from django.contrib.auth import get_user_model
from pages.flex_permissions import CanDraftFlexPages

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


from pages.flex_drafts import (
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
