from http import cookies

from django.test import TestCase, Client
from wagtail.test.utils import WagtailTestUtils

from shared.test_utilities import mock_user_login


class AdminPages(TestCase, WagtailTestUtils):

    def setUp(self):
        self.client = Client()

    @property
    def target(self):
        def test_redirect(path):
            response = self.client.get(path)
            self.assertIn(response.status_code, (301, 302))
            return response

        return test_redirect

    def test_admin_link(self):
        self.target('/admin/')

    def test_slashless_admin_link(self):
        self.target('/admin')

    def test_images_link(self):
        self.target('/admin/images/')

    def test_pages_link(self):
        self.target('/admin/pages/')

    def test_documents_link(self):
        self.target('/admin/documents/')

    def test_snippets_link(self):
        self.target('/admin/snippets/')

    def test_users_link(self):
        self.target('/admin/users/')

    def test_groups_link(self):
        self.target('/admin/groups/')

    # A lazy test of our search field without parsing html
    def test_admin_search(self):
        response = self.client.get('/admin/pages/search/?q=openstax')
        self.assertEqual(response.status_code, 302)
