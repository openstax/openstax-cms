from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils, WagtailPageTests
from wagtail.wagtailcore.models import Page
from pages.models import (HomePage,
                          HigherEducation,
                          K12,
                          Products,
                          Research,
                          ContactUs,
                          AboutUs,
                          Give,
                          AdoptionForm,
                          Adopters,
                          EcosystemAllies)
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
                            header_2_text="Header Text",
                            higher_ed_heading="Higher Ed Heading",
                            higher_ed_description="Higher Ed Description",
                            k12_heading="K12 Heading",
                            k12_description="K12 Description",
                            give_heading="Give Heading",
                            give_description="Give Description",
                            give_cta_link="http://giving.rice.edu",
                            give_cta_text="Give CTA",
                            adopter_heading="Adopter Heading",
                            adopter_description="Adopter Description",
                            adopter_cta_link="http://example.rice.edu",
                            adopter_cta_text="Adopter CTA"
                            )
        root_page.add_child(instance=homepage)

        retrieved_page = Page.objects.get(id=homepage.id)
        self.assertEqual(retrieved_page.title, "Hello World")

    def test_allowed_subpages(self):
        self.assertAllowedSubpageTypes(HomePage, {
            HigherEducation,
            K12,
            Products,
            Research,
            ContactUs,
            AboutUs,
            Give,
            AdoptionForm,
            Adopters,
            EcosystemAllies,
            Ally,
            NewsIndex,
            BookIndex
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

