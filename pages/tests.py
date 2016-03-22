from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils
from wagtail.wagtailredirects.models import Redirect


class TestPages(TestCase, WagtailTestUtils):

    def setUp(self):
        self.login()

    def test_homepage_return_correct_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_osc_redirect_link_migrations(self):
        self.assertEqual(Redirect.objects.count(), 2029)
        redirect = Redirect.objects.first()
        start_link = redirect.old_path  # redirect field name is misleading
        redirect_link = redirect.link
        response = self.client.get(start_link)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, redirect_link)


class AdminPages(TestCase, WagtailTestUtils):

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
        self.assertIn(b'Sorry, no pages match', response.content)

