import json

from django.test import TestCase
from django.urls import reverse
from wagtail.test.utils import WagtailPageTestCase, WagtailTestUtils
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


class OXMenusNodeModelTest(TestCase):
    def test_region_defaults_to_main(self):
        m = Menus.objects.create(name="Products")
        self.assertEqual(m.region, "main")

    def test_node_type_precedence(self):
        # dynamic wins over everything
        dynamic = Menus(name="User", component_key="user-menu", partial_url="/x")
        self.assertEqual(dynamic.node_type(), "dynamic")
        # link when partial_url set and no component
        link = Menus(name="K12", partial_url="/k12")
        self.assertEqual(link.node_type(), "link")
        # dropdown otherwise
        dropdown = Menus(name="About")
        self.assertEqual(dropdown.node_type(), "dropdown")


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


class OXMenusSerializerShapeTest(TestCase):
    def _serialize(self, m):
        from oxmenus.serializers import OXMenusSerializer
        return OXMenusSerializer(m).data

    def test_dynamic_node_shape(self):
        m = Menus.objects.create(name="Hi", region="utility",
                                 component_key="user-menu")
        data = self._serialize(m)
        self.assertEqual(data["type"], "dynamic")
        self.assertEqual(data["component"], "user-menu")
        self.assertEqual(data["region"], "utility")
        self.assertEqual(data["label"], "Hi")

    def test_link_node_shape(self):
        m = Menus.objects.create(name="K12", region="utility",
                                 partial_url="/k12")
        data = self._serialize(m)
        self.assertEqual(data["type"], "link")
        self.assertEqual(data["partial_url"], "/k12")
        self.assertEqual(data["region"], "utility")
        self.assertNotIn("component", data)

    def test_dropdown_node_includes_region(self):
        m = Menus.objects.create(name="About", region="main")
        data = self._serialize(m)
        self.assertEqual(data["type"], "dropdown")
        self.assertEqual(data["region"], "main")
        self.assertIn("menu", data)


class OXMenusAdminScopingTest(WagtailTestUtils, TestCase):
    def setUp(self):
        self.login()  # creates + logs in a superuser
        Menus.objects.create(name="Footer Help", region="footer",
                             partial_url="/help")
        Menus.objects.create(name="Main About", region="main")

    def test_footer_index_lists_only_footer_menus(self):
        resp = self.client.get(reverse("footer_menu:index"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Footer Help")
        self.assertNotContains(resp, "Main About")

    def test_footer_add_defaults_region(self):
        resp = self.client.get(reverse("footer_menu:add"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<option value="footer" selected')

    # C1 regression: reorder view must be scoped to the region so dragging
    # within footer does not touch sort_order values for main (or other) items.
    def test_reorder_queryset_is_region_scoped(self):
        from oxmenus.admin_views import RegionReorderView
        from unittest.mock import patch

        # Create two footer items and one main item with known sort_order values.
        footer1 = Menus.objects.create(name="Footer 1", region="footer", sort_order=1)
        footer2 = Menus.objects.create(name="Footer 2", region="footer", sort_order=2)
        main1 = Menus.objects.create(name="Main 1", region="main", sort_order=10)

        view = RegionReorderView()
        view.region = "footer"
        view.model = Menus
        view.sort_order_field = "sort_order"

        qs = view.get_queryset()
        pks = list(qs.values_list("pk", flat=True))

        self.assertIn(footer1.pk, pks)
        self.assertIn(footer2.pk, pks)
        self.assertNotIn(main1.pk, pks,
                         "Main item should be excluded from footer reorder queryset")

    # I1: utility index must not show footer items; main add must pre-select "main".
    def test_utility_index_excludes_footer_item(self):
        resp = self.client.get(reverse("utility_menu:index"))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Footer Help")

    def test_main_add_defaults_region_to_main(self):
        resp = self.client.get(reverse("main_menu:add"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<option value="main" selected')
