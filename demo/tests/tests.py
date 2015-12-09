from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils


class TestPages(TestCase, WagtailTestUtils):
    fixtures = ['site.json']

    def setUp(self):
        self.login()

    def test_homepage_return_correct_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class AdminPages(TestCase, WagtailTestUtils):
    fixtures = ['site.json']

    def setUp(self):
        self.login()

    @property
    def target(self):
        def test_redirect(path):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 301)
            perm_redirect_url = response.url
            response = self.client.get(perm_redirect_url)
            self.assertEqual(response.status_code, 200)
            return response
        return test_redirect

    def test_admin_link(self):
        self.target('/admin')

    def test_images_link(self):
        self.target('/admin/images')

    def test_pages_link(self):
        self.target('/admin/pages')

    def test_documents_link(self):
        self.target('/admin/documents')

    def test_snippets_link(self):
        self.target('/admin/snippets')

    def test_users_link(self):
        self.target('/admin/users')

    def test_groups_link(self):
        self.target('/admin/groups')

    # A lazy test of our search field without parsing html
    def test_admin_search(self):
        response = self.client.get('/admin/pages/search/?q=openstax')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Openstax College',response.content)
        self.assertIn('About Openstax',response.content)

