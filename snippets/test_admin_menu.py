"""Tests for the reorganised Wagtail admin menu: snippet grouping, retired
modeladmins now served by ModelViewSets, and GiveToday moved to Settings."""
from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from wagtail.snippets.models import get_snippet_models

from snippets.models import (
    Subject,
    FacultyResource,
    SharedContent,
    ErrataContent,
    WebinarCollection,
)


class SnippetRegistrationTests(TestCase):
    def test_snippets_still_registered_after_grouping(self):
        models = get_snippet_models()
        for model in (Subject, FacultyResource, SharedContent, ErrataContent, WebinarCollection):
            self.assertIn(model, models)

    def test_models_module_does_not_double_register(self):
        # Registration now lives in snippets/wagtail_hooks.py via viewset groups;
        # models.py must not also call register_snippet (that would double-register).
        import inspect
        import snippets.models as snippet_models

        source = inspect.getsource(snippet_models)
        self.assertNotIn("register_snippet(", source)


class ModelViewSetMenuTests(TestCase):
    def test_retired_modeladmins_now_have_viewset_urls(self):
        # Webinars, OX Menu, and the Site Messaging models moved off
        # wagtail_modeladmin onto ModelViewSets.
        for url_name in (
            "webinars:index",
            "oxmenus:index",
            "donationpopup:index",
            "donationlink:index",
            "fundraiser:index",
            "sitebanner:index",
        ):
            try:
                reverse(url_name)
            except NoReverseMatch:  # pragma: no cover
                self.fail(f"Expected viewset URL {url_name} to be registered")

    def test_partner_and_salesforce_data_groups_registered(self):
        for url_name in (
            "partners:index",
            "partner_types:index",
            "schools:index",
            "adoption_opportunities:index",
            "resource_downloads:index",
        ):
            try:
                reverse(url_name)
            except NoReverseMatch:  # pragma: no cover
                self.fail(f"Expected viewset URL {url_name} to be registered")


class MainMenuStructureTests(TestCase):
    def test_flat_snippets_menu_hidden_groups_present(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from wagtail.admin.menu import admin_menu

        user = User.objects.create_superuser("menuadmin", "m@openstax.org", "pw")
        request = RequestFactory().get("/admin/")
        request.user = user
        items = admin_menu.menu_items_for_request(request)
        names = [item.name for item in items]
        self.assertNotIn("snippets", names)  # flat catch-all hidden
        for group in ("subjects", "resources", "blog", "webinars", "reusable-content"):
            self.assertIn(group, names)
        self.assertNotIn("webinar-content", names)

    def test_content_quick_links_are_grouped_without_dead_sidebar_items(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from wagtail.admin.menu import admin_menu

        user = User.objects.create_superuser("contentadmin", "c@openstax.org", "pw")
        request = RequestFactory().get("/admin/")
        request.user = user

        items = admin_menu.menu_items_for_request(request)
        names = [item.name for item in items]
        self.assertIn("content", names)
        self.assertNotIn("books", names)
        self.assertNotIn("errata", names)
        self.assertNotIn("django-admin", names)

        content_item = next(item for item in items if item.name == "content")
        content_names = [
            item.name
            for item in sorted(
                content_item.menu.menu_items_for_request(request),
                key=lambda item: item.order,
            )
        ]
        self.assertEqual(["books", "errata", "redirects"], content_names)
        self.assertNotIn("errata-beta", content_names)

    def test_blog_menu_includes_blog_posts(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from wagtail.admin.menu import admin_menu

        user = User.objects.create_superuser("blogadmin", "blog@openstax.org", "pw")
        request = RequestFactory().get("/admin/")
        request.user = user

        items = admin_menu.menu_items_for_request(request)
        blog_item = next(item for item in items if item.name == "blog")
        blog_names = [
            item.name
            for item in sorted(
                blog_item.menu.menu_items_for_request(request),
                key=lambda item: item.order,
            )
        ]

        self.assertEqual(
            ["blog-posts", "blog-collections", "blog-content-types", "news-sources"],
            blog_names,
        )

    def test_webinars_menu_combines_events_and_content(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from wagtail.admin.menu import admin_menu

        user = User.objects.create_superuser("webinaradmin", "w@openstax.org", "pw")
        request = RequestFactory().get("/admin/")
        request.user = user

        items = admin_menu.menu_items_for_request(request)
        names = [item.name for item in items]
        self.assertIn("webinars", names)
        self.assertNotIn("webinar-content", names)

        webinars_item = next(item for item in items if item.name == "webinars")
        webinar_names = [
            item.name
            for item in sorted(
                webinars_item.menu.menu_items_for_request(request),
                key=lambda item: item.order,
            )
        ]

        self.assertEqual(
            ["webinars", "webinar-collections", "no-webinar-message"],
            webinar_names,
        )

    def test_books_listing_renders(self):
        from django.contrib.auth.models import User
        from django.urls import reverse

        self.client.force_login(
            User.objects.create_superuser("booksadmin", "b@openstax.org", "pw")
        )
        response = self.client.get(reverse("books:index"))
        self.assertEqual(response.status_code, 200)


class GivingGroupMenuTests(TestCase):
    """Donation Popup, Donation Links, and Fundraisers moved into a new
    top-level "Giving" group so donation-related admin is findable in one
    place; Give Today (a BaseSiteSetting) gets a deep-link item beside it."""

    def test_giving_group_registered_with_expected_items(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from wagtail.admin.menu import admin_menu

        user = User.objects.create_superuser("givingadmin", "giving@openstax.org", "pw")
        request = RequestFactory().get("/admin/")
        request.user = user

        items = admin_menu.menu_items_for_request(request)
        names = [item.name for item in items]
        self.assertIn("giving", names)
        self.assertIn("give-today-settings", names)

        giving_item = next(item for item in items if item.name == "giving")
        giving_names = [
            item.name
            for item in sorted(
                giving_item.menu.menu_items_for_request(request),
                key=lambda item: item.order,
            )
        ]
        self.assertEqual(["donation-popup", "donation-links", "fundraisers"], giving_names)

    def test_site_messaging_no_longer_holds_donation_popup_or_fundraisers(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from wagtail.admin.menu import admin_menu

        user = User.objects.create_superuser("sitemsgadmin", "sm@openstax.org", "pw")
        request = RequestFactory().get("/admin/")
        request.user = user

        items = admin_menu.menu_items_for_request(request)
        site_messaging = next(item for item in items if item.name == "site-messaging")
        site_messaging_names = [
            item.name for item in site_messaging.menu.menu_items_for_request(request)
        ]
        self.assertEqual(["site-banners"], site_messaging_names)

    def test_give_today_settings_menu_item_links_to_settings_edit_page(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from django.urls import reverse
        from wagtail.admin.menu import admin_menu

        from global_settings.models import GiveToday

        user = User.objects.create_superuser("givetodayadmin", "gt@openstax.org", "pw")
        request = RequestFactory().get("/admin/")
        request.user = user

        items = admin_menu.menu_items_for_request(request)
        give_today_item = next(item for item in items if item.name == "give-today-settings")
        expected_url = reverse(
            "wagtailsettings:edit", args=(GiveToday._meta.app_label, GiveToday._meta.model_name)
        )
        self.assertEqual(give_today_item.url, expected_url)

    def test_footer_give_link_menu_item_links_to_settings_edit_page(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from django.urls import reverse
        from wagtail.admin.menu import admin_menu

        from global_settings.models import Footer

        user = User.objects.create_superuser("footeradmin", "footer@openstax.org", "pw")
        request = RequestFactory().get("/admin/")
        request.user = user

        items = admin_menu.menu_items_for_request(request)
        names = [item.name for item in items]
        self.assertIn("footer-give-link-settings", names)

        footer_item = next(item for item in items if item.name == "footer-give-link-settings")
        expected_url = reverse(
            "wagtailsettings:edit", args=(Footer._meta.app_label, Footer._meta.model_name)
        )
        self.assertEqual(footer_item.url, expected_url)

    def test_giving_menu_items_are_adjacent_and_ordered(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from wagtail.admin.menu import admin_menu

        user = User.objects.create_superuser("orderadmin", "order@openstax.org", "pw")
        request = RequestFactory().get("/admin/")
        request.user = user

        items = admin_menu.menu_items_for_request(request)
        ordered = [item.name for item in sorted(items, key=lambda item: item.order)]
        start = ordered.index("giving")

        self.assertEqual(
            ["giving", "give-today-settings", "footer-give-link-settings"],
            ordered[start:start + 3],
        )


class GiveTodaySettingTests(TestCase):
    def test_give_today_registered_as_setting(self):
        from wagtail.contrib.settings.registry import registry
        from global_settings.models import GiveToday

        self.assertIn(GiveToday, registry)
