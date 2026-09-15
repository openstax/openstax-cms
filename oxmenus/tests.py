import json

from django.test import TestCase
from wagtail.test.utils import WagtailPageTestCase
from oxmenus.models import Menus


class OXMenuTests(WagtailPageTestCase, TestCase):
    def setUp(self):
        oxmenu = Menus(name="What we do",
                        menu=json.dumps(
                            [{"id": "07d57c52-5ec0-494e-870f-3e8b6c86aebc", "type": "menu_block", "value": {
                                "menu_items": [{"id": "c2793dd0-d0d2-4835-ad1a-3431fd435604", "type": "item",
                                                "value": {"label": "About Us", "partial_url": "/about"}},
                                               {"id": "7d5e6a0d-8034-43c5-89b6-2de10f534034", "type": "item",
                                                "value": {"label": "Team", "partial_url": "/team"}},
                                               {"id": "a402ea4e-cef1-4257-adce-cc4cd1be7f5e", "type": "item",
                                                "value": {"label": "Research", "partial_url": "/research"}}]}}]
                        )
                        )
        oxmenu.save()

    def test_all_menus(self):
        response = self.client.get('/apps/cms/api/oxmenus/')
        self.assertContains(response, 'About Us')
        self.assertContains(response, 'Research')


class OXMenusOrderingTest(TestCase):
    def test_api_returns_menus_in_sort_order(self):
        # Create out of order; lowest sort_order should come first.
        Menus.objects.create(name="Third", partial_url="/third", sort_order=30)
        Menus.objects.create(name="First", partial_url="/first", sort_order=10)
        Menus.objects.create(name="Second", partial_url="/second", sort_order=20)

        response = self.client.get('/apps/cms/api/oxmenus/')
        labels = [item["label"] for item in response.json()]
        self.assertEqual(labels, ["First", "Second", "Third"])


class OXMenusFlagAwareTest(TestCase):
    def _menu(self):
        m = Menus(
            name="Products",
            key="products-dropdown",
            feature_flag="",
            flag_value="",
            menu=json.dumps([
                {
                    "id": "aaa00000-0000-0000-0000-000000000001",
                    "type": "menu_block",
                    "value": {
                        "menu_items": [
                            {
                                "id": "bbb00000-0000-0000-0000-000000000001",
                                "type": "item",
                                "value": {
                                    "label": "For K12 Teachers",
                                    "partial_url": "/k12",
                                    "key": "k12-teachers",
                                    "feature_flag": "nav-k12-item",
                                    "flag_value": "",
                                },
                            },
                            {
                                "id": "bbb00000-0000-0000-0000-000000000002",
                                "type": "item",
                                "value": {
                                    "label": "Assignable",
                                    "partial_url": "/assignable",
                                },
                            },
                        ]
                    },
                }
            ]),
        )
        m.save()
        return m

    def test_menu_block_json_includes_new_fields_and_keeps_old(self):
        items = self._menu().menu_block_json()
        first = items[0]
        # backward-compatible keys still present
        self.assertEqual(first["label"], "For K12 Teachers")
        self.assertEqual(first["partial_url"], "/k12")
        # new additive keys
        self.assertEqual(first["key"], "k12-teachers")
        self.assertEqual(first["feature_flag"], "nav-k12-item")
        self.assertEqual(first["flag_value"], "")
        # an item with no flag metadata still serializes with empty strings
        self.assertEqual(items[1]["feature_flag"], "")

    def test_serializer_exposes_dropdown_level_flag_fields(self):
        from oxmenus.serializers import OXMenusSerializer
        data = OXMenusSerializer(self._menu()).data
        self.assertEqual(data["name"], "Products")
        self.assertEqual(data["key"], "products-dropdown")
        self.assertIn("feature_flag", data)
        self.assertIn("flag_value", data)
        self.assertEqual(data["menu"][0]["key"], "k12-teachers")


class OXMenusLinkModeTest(TestCase):
    def test_link_mode_record_serializes_as_link_node(self):
        from oxmenus.serializers import OXMenusSerializer
        m = Menus.objects.create(
            name="For K12 Teachers",
            partial_url="/k12",
            key="k12-teachers",
            feature_flag="nav-k12-item",
        )
        data = OXMenusSerializer(m).data
        self.assertEqual(data["label"], "For K12 Teachers")
        self.assertEqual(data["partial_url"], "/k12")
        self.assertEqual(data["key"], "k12-teachers")
        self.assertEqual(data["feature_flag"], "nav-k12-item")
        # a link node is NOT a dropdown
        self.assertNotIn("menu", data)
        self.assertNotIn("name", data)

    def test_dropdown_record_unchanged_when_no_partial_url(self):
        from oxmenus.serializers import OXMenusSerializer
        m = Menus.objects.create(
            name="Products",
            key="products-dropdown",
            menu=json.dumps([
                {
                    "id": "ccc00000-0000-0000-0000-000000000001",
                    "type": "menu_block",
                    "value": {
                        "menu_items": [
                            {
                                "id": "ddd00000-0000-0000-0000-000000000001",
                                "type": "item",
                                "value": {
                                    "label": "Assignable",
                                    "partial_url": "/assignable",
                                },
                            },
                        ]
                    },
                }
            ]),
        )
        data = OXMenusSerializer(m).data
        self.assertEqual(data["name"], "Products")
        self.assertIn("menu", data)
        self.assertNotIn("label", data)
        self.assertNotIn("partial_url", data)


class OXMenusPlacementFilterTest(TestCase):
    """The no-param case is a back-compat guarantee: the currently-deployed
    frontend calls /oxmenus/ with no query string and must keep getting header
    rows only, even though the table now also holds footer rows."""

    def setUp(self):
        # Start from a clean slate: the 0013 data migration already seeded real
        # footer columns, which would otherwise show up alongside these fixtures.
        Menus.objects.all().delete()
        Menus.objects.create(name="Header One", partial_url="/one", sort_order=10, placement="header")
        Menus.objects.create(name="Header Two", partial_url="/two", sort_order=20, placement="header")
        Menus.objects.create(name="Footer One", partial_url="/f-one", sort_order=10, placement="footer")
        Menus.objects.create(name="Footer Two", partial_url="/f-two", sort_order=20, placement="footer")

    def test_no_param_returns_header_only(self):
        response = self.client.get('/apps/cms/api/oxmenus/')
        labels = [item["label"] for item in response.json()]
        self.assertEqual(labels, ["Header One", "Header Two"])

    def test_explicit_header_param_matches_no_param(self):
        response = self.client.get('/apps/cms/api/oxmenus/?placement=header')
        labels = [item["label"] for item in response.json()]
        self.assertEqual(labels, ["Header One", "Header Two"])

    def test_footer_param_returns_footer_only_in_sort_order(self):
        response = self.client.get('/apps/cms/api/oxmenus/?placement=footer')
        labels = [item["label"] for item in response.json()]
        self.assertEqual(labels, ["Footer One", "Footer Two"])

    def test_unrecognized_placement_falls_back_to_header(self):
        response = self.client.get('/apps/cms/api/oxmenus/?placement=bogus')
        labels = [item["label"] for item in response.json()]
        self.assertEqual(labels, ["Header One", "Header Two"])

    def test_translated_rows_are_not_served_alongside_their_source(self):
        from wagtail.models import Locale

        spanish = Locale.objects.create(language_code="es")
        Menus.objects.create(
            name="Encabezado Uno", partial_url="/uno", sort_order=10,
            placement="header", locale=spanish
        )

        labels = [
            item["label"]
            for item in self.client.get('/apps/cms/api/oxmenus/').json()
        ]

        self.assertEqual(labels, ["Header One", "Header Two"])

    def test_locale_param_selects_the_translated_rows(self):
        from wagtail.models import Locale

        spanish = Locale.objects.create(language_code="es")
        Menus.objects.create(
            name="Encabezado Uno", partial_url="/uno", sort_order=10,
            placement="header", locale=spanish
        )

        labels = [
            item["label"]
            for item in self.client.get('/apps/cms/api/oxmenus/?locale=es').json()
        ]

        self.assertEqual(labels, ["Encabezado Uno"])

    def test_unknown_locale_falls_back_to_the_default(self):
        labels = [
            item["label"]
            for item in self.client.get('/apps/cms/api/oxmenus/?locale=zz').json()
        ]

        self.assertEqual(labels, ["Header One", "Header Two"])


class PlacementFormScopingTest(TestCase):
    """`placement` must not be editable: the queryset is scoped, so a row moved to
    the other nav would vanish from its list and be served by the wrong menu."""

    def setUp(self):
        from django.contrib.auth.models import User

        self.user = User.objects.create_superuser("placementadmin", "pa@openstax.org", "pw")
        self.client.force_login(self.user)

    def test_placement_is_not_an_editable_form_field(self):
        from oxmenus.wagtail_hooks import FooterMenusViewSet, HeaderMenusViewSet

        for viewset in (HeaderMenusViewSet, FooterMenusViewSet):
            self.assertIn("placement", viewset.exclude_form_fields)

    def test_create_view_forces_its_own_placement(self):
        from django.test import RequestFactory

        from oxmenus.wagtail_hooks import FooterMenusCreateView, HeaderMenusCreateView

        class _StubForm:
            """Stands in for the real ModelForm, whose StreamField makes a full POST
            unwieldy. save_instance() is the hook under test."""

            def __init__(self, instance):
                self.instance = instance

            def save(self):
                self.instance.save()
                return self.instance

        for view_class, expected in (
            (HeaderMenusCreateView, 'header'),
            (FooterMenusCreateView, 'footer'),
        ):
            view = view_class()
            view.request = RequestFactory().post('/admin/')
            view.request.user = self.user
            # a row arriving marked for the other nav must not stay that way
            other = 'footer' if expected == 'header' else 'header'
            view.form = _StubForm(
                Menus(name=f'Added {expected}', sort_order=40,
                      key=f'added-{expected}', placement=other, menu=[])
            )

            view.save_instance()

            created = Menus.objects.get(key=f'added-{expected}')
            self.assertEqual(expected, created.placement)


class FooterSettingsMenuTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory

        self.request = RequestFactory().get('/admin/')
        self.request.user = User.objects.create_superuser(
            "settingsadmin", "sa@openstax.org", "pw"
        )

    def test_footer_is_no_longer_duplicated_in_the_settings_menu(self):
        from wagtail.admin.menu import settings_menu

        names = [
            item.name for item in settings_menu.menu_items_for_request(self.request)
        ]

        self.assertNotIn("footer", names)

    def test_the_footer_settings_page_is_still_reachable(self):
        from django.urls import reverse

        from global_settings.models import Footer

        self.client.force_login(self.request.user)
        # Wagtail redirects this to the site-scoped edit URL, so follow it.
        response = self.client.get(
            reverse(
                "wagtailsettings:edit",
                args=(Footer._meta.app_label, Footer._meta.model_name),
            ),
            follow=True,
        )

        self.assertEqual(200, response.status_code)


class SeededFooterMenusTest(TestCase):
    """The 0013 data migration seeds Help/OpenStax/Policies footer columns on
    every environment (mirroring the hardcoded os-webview JSX); assert the API
    still serves exactly what was seeded."""

    def test_seeded_columns_and_order(self):
        response = self.client.get('/apps/cms/api/oxmenus/?placement=footer')
        data = response.json()
        self.assertEqual([d["name"] for d in data], ["Help", "OpenStax", "Policies"])

    def test_help_column_labels_and_urls(self):
        response = self.client.get('/apps/cms/api/oxmenus/?placement=footer')
        help_column = next(d for d in response.json() if d["name"] == "Help")
        self.assertEqual(
            [(item["label"], item["partial_url"]) for item in help_column["menu"]],
            [
                ("Contact Us", "/contact"),
                ("Support Center", "https://help.openstax.org/s/"),
                ("FAQ", "/faq"),
                ("Order Print", "/print/"),
                ("System Status", "https://status.openstax.org/"),
            ],
        )

    def test_openstax_column_labels_and_urls(self):
        response = self.client.get('/apps/cms/api/oxmenus/?placement=footer')
        column = next(d for d in response.json() if d["name"] == "OpenStax")
        self.assertEqual(
            [(item["label"], item["partial_url"]) for item in column["menu"]],
            [
                ("Press", "/press"),
                ("Newsletter", "http://www2.openstax.org/l/218812/2016-10-04/lvk"),
                ("Careers", "/careers"),
            ],
        )

    def test_policies_column_labels_and_urls(self):
        response = self.client.get('/apps/cms/api/oxmenus/?placement=footer')
        column = next(d for d in response.json() if d["name"] == "Policies")
        self.assertEqual(
            [(item["label"], item["partial_url"]) for item in column["menu"]],
            [
                ("Accessibility Statement", "/accessibility-statement"),
                ("Terms of Use", "/tos"),
                ("Licensing", "/license"),
                ("Privacy Notice", "/privacy"),
            ],
        )


class OXMenusAdminMenuTests(TestCase):
    """The old flat "OX Menu" top-level item is replaced by Header/Footer
    groups (see oxmenus/wagtail_hooks.py)."""

    def _menu_items_for(self, user):
        from django.test import RequestFactory
        from wagtail.admin.menu import admin_menu

        request = RequestFactory().get('/admin/')
        request.user = user
        return admin_menu.menu_items_for_request(request)

    def test_header_and_footer_groups_registered_and_ox_menu_gone(self):
        from django.contrib.auth.models import User

        user = User.objects.create_superuser("oxmenuadmin", "oxmenuadmin@openstax.org", "pw")
        items = self._menu_items_for(user)
        names = [item.name for item in items]

        self.assertIn("header", names)
        self.assertIn("footer", names)
        self.assertNotIn("ox-menu", names)
        self.assertNotIn("oxmenus", names)

    def test_header_group_contains_menus_item(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory

        user = User.objects.create_superuser("headermenuadmin", "headermenuadmin@openstax.org", "pw")
        request = RequestFactory().get('/admin/')
        request.user = user
        items = self._menu_items_for(user)
        header_item = next(item for item in items if item.name == "header")
        sub_names = [i.name for i in header_item.menu.menu_items_for_request(request)]
        self.assertIn("headermenus", sub_names)

    def test_footer_group_contains_menus_item_and_footer_content_link(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory

        user = User.objects.create_superuser("footermenuadmin", "footermenuadmin@openstax.org", "pw")
        request = RequestFactory().get('/admin/')
        request.user = user
        items = self._menu_items_for(user)
        footer_item = next(item for item in items if item.name == "footer")
        sub_names = [i.name for i in footer_item.menu.menu_items_for_request(request)]
        self.assertIn("footermenus", sub_names)
        self.assertIn("footer-content-settings", sub_names)

    def test_footer_content_link_hidden_without_change_permission(self):
        from django.contrib.auth.models import User
        from django.test import RequestFactory

        staffer = User.objects.create_user(
            "nopermstaffer", "nopermstaffer@openstax.org", "pw", is_staff=True,
        )
        request = RequestFactory().get('/admin/')
        request.user = staffer

        from global_settings.models import Footer
        from oxmenus.wagtail_hooks import SettingsLinkMenuItem

        # Staff without change permission on Footer must not be offered the
        # deep-link, or clicking it 403s.
        link = SettingsLinkMenuItem("Footer Content", Footer, name="footer-content-settings")
        self.assertFalse(link.is_shown(request))

        # And it must not reach the rendered menu either.
        names = [item.name for item in self._menu_items_for(staffer)]
        self.assertNotIn("footer-content-settings", names)
