from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils, WagtailPageTests
from wagtail.core.models import Page
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
                          FAQ,
                          Support,
                          GiveForm,
                          Accessibility,
                          Licensing,
                          CompCopy,
                          AdoptForm,
                          InterestForm,
                          Marketing,
                          Technology,
                          ErrataList,
                          PrivacyPolicy,
                          PrintOrder)
from allies.models import Ally
from news.models import NewsIndex, PressIndex
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
            PressIndex,
            BookIndex,
            FoundationSupport,
            OurImpact,
            Give,
            TermsOfService,
            AP,
            FAQ,
            Support,
            GiveForm,
            Accessibility,
            Licensing,
            CompCopy,
            AdoptForm,
            InterestForm,
            Marketing,
            Technology,
            ErrataList,
            PrivacyPolicy,
            PrintOrder
        })

class PageTests(WagtailPageTests):
    def setUp(self):
        pass

    def test_api_redirect(self):
        pages = Page.objects.all()
        for page in pages:
            response = self.client.get('/api/pages/{}'.format(page.slug))
            self.assertNotEquals(response.status_code, 404)



class ErrataListTest(WagtailPageTests):

    def test_can_create_errata_list_page(self):
        root_page = Page.objects.get(title="Root")
        homepage = HomePage(title="Hello World",
                            slug="hello-world",
                            )
        root_page.add_child(instance=homepage)
        errata_list_page = ErrataList(title="Errata List Template",
                                      correction_schedule="Some sample correction schedule text.")
        homepage.add_child(instance=errata_list_page)

        retrieved_page = Page.objects.get(id=errata_list_page.id)
        self.assertEqual(retrieved_page.title, "Errata List Template")


class AdminPages(TestCase, WagtailTestUtils):

    def setUp(self):
        self.login()

    @property
    def target(self):
        def test_redirect(path):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            return response
        return test_redirect

    def test_admin_link(self):
        self.target('/admin/')

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
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sorry, no pages match', response.content)
