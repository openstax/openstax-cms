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
            # oxmenus moved again, ModelViewSet -> SnippetViewSet (for
            # wagtail-transfer sync); snippet index views are named "list".
            "oxmenus:list",
            "donationpopup:index",
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


class GiveTodaySettingTests(TestCase):
    def test_give_today_registered_as_setting(self):
        from wagtail.contrib.settings.registry import registry
        from global_settings.models import GiveToday

        self.assertIn(GiveToday, registry)
