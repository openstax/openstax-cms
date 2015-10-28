from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils


class TestPages(TestCase, WagtailTestUtils):
    fixtures = ['site.json']

    def setUp(self):
        self.login()

    def test_homepage_return_correct_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)