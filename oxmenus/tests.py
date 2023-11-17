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
