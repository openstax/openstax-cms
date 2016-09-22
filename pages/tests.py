from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils, WagtailPageTests
from wagtail.wagtailcore.models import Page
from pages.models import (HomePage,
                          HigherEducation,
                          ContactUs,
                          AboutUs,
                          GeneralPage,
                          EcosystemAllies,
                          FoundationSupport,
                          OurImpact,
                          Give,
                          TermsOfService,
                          AP,
                          FAQ)
from allies.models import Ally
from news.models import NewsIndex
from books.models import BookIndex


class HomePageTests(WagtailPageTests):

    def test_cant_create_homepage_under_homepage(self):
        self.assertCanNotCreateAt(HomePage, HomePage)

    def test_homepage_return_correct_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_can_create_homepage(self):
        root_page = Page.objects.get(title="Root")
        homepage = HomePage(title="Hello World",
                            slug="hello-world",
                            )
        root_page.add_child(instance=homepage)

        retrieved_page = Page.objects.get(id=homepage.id)
        self.assertEqual(retrieved_page.title, "Hello World")

    def test_allowed_subpages(self):
        self.assertAllowedSubpageTypes(HomePage, {
            HigherEducation,
            ContactUs,
            AboutUs,
            GeneralPage,
            EcosystemAllies,
            Ally,
            NewsIndex,
            BookIndex,
            FoundationSupport,
            OurImpact,
            Give,
            TermsOfService,
            AP,
            FAQ,
        })


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

