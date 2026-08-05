# pages/tests/test_promote_home.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page, Site

from pages import models as page_models
from salesforce.models import School

from pages.promote_home import (
    promote_to_home,
    HomePageNotFound,
    HomePageLocked,
    PromotePermissionDenied,
)

LANDING_LAYOUT = [{"type": "landing", "value": {"nav_links": [], "show_give_now_button": True}}]
HERO_BODY = [{"type": "hero", "value": {"content": [], "image": None, "image_alt": "Alt", "config": []}}]
DRAFT_HERO_BODY = [{"type": "hero", "value": {"content": [], "image": None, "image_alt": "Draft Alt", "config": []}}]


class PromoteHomeTestBase(TestCase):
    def setUp(self):
        root = Page.objects.get(depth=1)
        self.home = page_models.RootPage(title="Home", slug="site-root")
        root.add_child(instance=self.home)

        site = Site.objects.get(is_default_site=True)
        site.root_page = self.home
        site.save()
        Site.clear_site_root_paths_cache()

        self.school = School.objects.create(name="Test School")
        self.image = Image.objects.create(title="Test Image", file=get_test_image_file())

        self.flex = page_models.FlexPage(
            title="Flex", slug="flex-page",
            layout=LANDING_LAYOUT,
            body=HERO_BODY,
            school=self.school,
            promote_image=self.image,
            seo_title="Flex SEO Title",
            search_description="Flex search description",
        )
        self.home.add_child(instance=self.flex)

        self.staff = get_user_model().objects.create_user(
            username="promoter", password="x", is_staff=True, is_superuser=True,
        )


class PromoteFieldCopyTests(PromoteHomeTestBase):
    def test_copies_all_promoted_fields_and_leaves_no_revisions_case_uncrashed(self):
        # self.flex has never had save_revision() called on it -- exercises the
        # "no revisions on the FlexPage" path (get_latest_revision_as_object
        # falls back to the live object).
        self.assertIsNone(self.flex.get_latest_revision())

        revision = promote_to_home(self.flex, self.staff)
        promoted = revision.as_object()

        # .raw_data is a lazy RawDataView; == across two views doesn't work
        # elementwise, so compare as plain lists.
        self.assertEqual(list(promoted.layout.raw_data), list(self.flex.layout.raw_data))
        self.assertEqual(list(promoted.body.raw_data), list(self.flex.body.raw_data))
        self.assertEqual(promoted.school_id, self.school.id)
        self.assertEqual(promoted.promote_image_id, self.image.id)
        self.assertEqual(promoted.seo_title, "Flex SEO Title")
        self.assertEqual(promoted.search_description, "Flex search description")

    def test_title_and_slug_untouched(self):
        revision = promote_to_home(self.flex, self.staff)
        promoted = revision.as_object()

        self.assertEqual(promoted.title, "Home")
        self.assertEqual(promoted.slug, "site-root")


class PromoteDraftOnlyTests(PromoteHomeTestBase):
    def test_live_root_unchanged_and_draft_recorded(self):
        promote_to_home(self.flex, self.staff)

        live_root = page_models.RootPage.objects.get(pk=self.home.pk)
        self.assertEqual(list(live_root.layout.raw_data), [])
        self.assertEqual(list(live_root.body.raw_data), [])
        self.assertIsNone(live_root.school_id)
        self.assertIsNone(live_root.promote_image_id)
        self.assertEqual(live_root.seo_title, "")
        self.assertTrue(live_root.has_unpublished_changes)
        self.assertIsNotNone(live_root.get_latest_revision())


class PromoteLatestRevisionSourceTests(PromoteHomeTestBase):
    def test_uses_flex_page_draft_content_not_live(self):
        # Give the FlexPage a draft that differs from what's on the live row.
        self.flex.body = DRAFT_HERO_BODY
        self.flex.save_revision(user=self.staff)  # draft only; not published

        fresh_flex = page_models.FlexPage.objects.get(pk=self.flex.pk)
        self.assertTrue(fresh_flex.has_unpublished_changes)

        revision = promote_to_home(fresh_flex, self.staff)
        promoted = revision.as_object()

        self.assertEqual(list(promoted.body.raw_data), DRAFT_HERO_BODY)


class PromoteLockTests(PromoteHomeTestBase):
    def test_locked_home_page_refuses_and_creates_no_revision(self):
        self.home.locked = True
        self.home.locked_by = self.staff
        self.home.save()

        with self.assertRaises(HomePageLocked):
            promote_to_home(self.flex, self.staff)

        live_root = page_models.RootPage.objects.get(pk=self.home.pk)
        self.assertIsNone(live_root.get_latest_revision())


class PromotePermissionTests(PromoteHomeTestBase):
    def test_user_without_edit_permission_is_denied(self):
        plain_user = get_user_model().objects.create_user(username="viewer", password="x")

        with self.assertRaises(PromotePermissionDenied):
            promote_to_home(self.flex, plain_user)

        live_root = page_models.RootPage.objects.get(pk=self.home.pk)
        self.assertIsNone(live_root.get_latest_revision())


class PromoteSiteRootTypeTests(PromoteHomeTestBase):
    def test_flex_page_as_site_root_is_not_exactly_rootpage(self):
        # A FlexPage is an MTI subclass of RootPage -- isinstance() would
        # wrongly accept it, so the site root must be rejected exactly here.
        site = Site.objects.get(is_default_site=True)
        site.root_page = self.flex
        site.save()
        Site.clear_site_root_paths_cache()

        with self.assertRaises(HomePageNotFound):
            promote_to_home(self.flex, self.staff)
