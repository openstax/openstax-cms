from django.test import TestCase
from django.urls import reverse
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailTestUtils

from pages.models import FlexPage, GeneralPage, RootPage


class PromoteToHomeAdminTests(TestCase, WagtailTestUtils):

    def setUp(self):
        wagtail_root = Page.objects.get(title="Root")

        self.home = RootPage(title="Home", slug="openstax-homepage")
        wagtail_root.add_child(instance=self.home)

        site = Site.objects.get(is_default_site=True)
        site.root_page = self.home
        site.save()

        self.flex_page = FlexPage(title="New Landing", slug="new-landing")
        self.home.add_child(instance=self.flex_page)

    def promote_url(self, page_id):
        return reverse('promote_to_home', args=[page_id])

    def test_get_confirm_renders_for_superuser(self):
        self.login()
        response = self.client.get(self.promote_url(self.flex_page.id))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New Landing")

    def test_post_creates_home_draft_revision_and_redirects(self):
        self.login()
        self.flex_page.seo_title = "Promoted SEO Title"
        self.flex_page.save_revision().publish()

        response = self.client.post(self.promote_url(self.flex_page.id))

        self.home.refresh_from_db()
        latest_revision = self.home.get_latest_revision()
        self.assertIsNotNone(latest_revision)
        self.assertEqual(latest_revision.as_object().seo_title, "Promoted SEO Title")
        self.assertRedirects(response, reverse('wagtailadmin_pages:edit', args=[self.home.id]))

    def test_non_flex_page_is_404(self):
        self.login()
        response = self.client.get(self.promote_url(self.home.id))
        self.assertEqual(response.status_code, 404)

        general_page = GeneralPage(title="General", slug="general")
        Page.objects.get(title="Root").add_child(instance=general_page)
        response = self.client.get(self.promote_url(general_page.id))
        self.assertEqual(response.status_code, 404)

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(self.promote_url(self.flex_page.id))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('wagtailadmin_login'), response.url)

    def test_locked_home_page_blocks_promotion_with_error(self):
        self.login()
        self.home.locked = True
        self.home.locked_by = None
        self.home.save()

        revision_count_before = self.home.revisions.count()
        response = self.client.post(self.promote_url(self.flex_page.id), follow=True)

        self.home.refresh_from_db()
        self.assertEqual(self.home.revisions.count(), revision_count_before)
        messages = list(response.context['messages'])
        self.assertTrue(any('locked' in str(m).lower() for m in messages))
