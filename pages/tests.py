from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils, WagtailPageTests
from wagtail.core.models import Page
from pages.models import (HomePage,
                          HigherEducation,
                          ContactUs,
                          AboutUsPage,
                          GeneralPage,
                          EcosystemAllies,
                          FoundationSupport,
                          OurImpact,
                          MapPage,
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
                          PrintOrder,
                          ResearchPage,
                          TeamPage,
                          Careers,
                          Rover,
                          RoverPage,
                          AnnualReportPage,
                          InstitutionalPartnership,
                          HeroJourneyPage,
                          InstitutionalPartnerProgramPage)
from allies.models import Ally
from news.models import NewsIndex, PressIndex
from books.models import BookIndex
from shared.test_utilities import assertPathDoesNotRedirectToTrailingSlash


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
            AboutUsPage,
            GeneralPage,
            EcosystemAllies,
            Ally,
            NewsIndex,
            PressIndex,
            BookIndex,
            FoundationSupport,
            OurImpact,
            MapPage,
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
            PrintOrder,
            ResearchPage,
            TeamPage,
            Careers,
            Rover,
            RoverPage,
            AnnualReportPage,
            InstitutionalPartnership,
            HeroJourneyPage,
            InstitutionalPartnerProgramPage
        })

        def test_can_create_ipp_page(self):
            root_page = Page.objects.get(title="Root")
            homepage = HomePage(title="Hello World",
                                slug="hello-world",
                                )
            root_page.add_child(instance=homepage)

            ipp_page = InstitutionalPartnerProgramPage(
                title="IPP Sample Page",
                section_1_heading="Heading",
                section_1_description="Description",
                section_1_link_text="Click me!",
                section_1_link="https://rice.edu",
                section_1_background_image=False,
                quote="Quote",
                quote_name="Author",
                quote_title="Title",
                quote_school="Rice University",
                section_2_heading="Heading 2",
                section_2_description="Description 2",
                section_2_image=None,
                section_2_image_alt="Alt",
                section_3_heading="Heading 3",
                section_3_description="Description 3",
                section_3_wide_cards=None,
                section_3_tall_cards=None,
                section_4_quote_text="Quote text",
                section_4_quote_name="Quote Name",
                section_4_quote_title="Quote title",
                section_4_quote_school="Rice University",
                section_4_background_image=None,
                section_5_heading="Heading 5",
                section_5_description="Description 5",
                section_5_image=None,
                section_5_image_alt="Alt",
                section_5_image_caption="Image caption",
                section_6_heading="Heading 6",
                section_6_description="Description 6",
                section_6_cards=None,
                section_7_heading="Heading 7",
                section_7_subheading="Subheading 7",
                section_7_icons=None,
                section_7_link_text="Click me",
                section_7_link_target="https://rice.edu",
                section_8_quote_text="Quote text",
                section_8_quote_name="Quote Name",
                section_8_quote_title="Quote title",
                section_8_quote_school="Rice University",
                section_9_heading="Heading 9",
                section_9_submit_url="https://rice.edu",
                section_9_form_prompt="Form here",
                section_9_button_text="Click me",
                section_9_contact_html="<b>Sample HTML</b>"
            )

            homepage.add_child(ipp_page)
            self.assertEqual(ipp_page.title, "IPP Sample Page")

class PageTests(WagtailPageTests):
    def setUp(self):
        pass

    def test_api_redirect(self):
        pages = Page.objects.all()
        for page in pages:
            response = self.client.get('/api/pages/{}'.format(page.slug))
            self.assertNotEquals(response.status_code, 404)

    def test_slashless_apis_are_good(self):
        assertPathDoesNotRedirectToTrailingSlash(self, '/api/pages/slug')
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/pages/slug')


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
