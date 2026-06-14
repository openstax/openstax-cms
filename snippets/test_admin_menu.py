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
        order_by_name = {item.name: item.order for item in items}
        self.assertNotIn("snippets", names)  # flat catch-all hidden
        for group in ("subjects", "resources", "blog", "webinar-content", "reusable-content"):
            self.assertIn(group, names)
        # Books sits as a sibling between Subjects and Resources (by menu order;
        # the menu is sorted by `order` at render time, not in this list).
        self.assertIn("books", names)
        self.assertLess(order_by_name["subjects"], order_by_name["books"])
        self.assertLess(order_by_name["books"], order_by_name["resources"])

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
