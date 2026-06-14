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
