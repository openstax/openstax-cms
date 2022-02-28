from django.test import TestCase
from django.core.management import call_command
from wagtail.tests.utils import WagtailTestUtils, WagtailPageTests
from wagtail.core.models import Page
from pages.models import (HomePage,
                          HigherEducation,
                          ContactUs,
                          AboutUsPage,
                          GeneralPage,
                          Supporters,
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
                          Technology,
                          ErrataList,
                          PrivacyPolicy,
                          PrintOrder,
                          ResearchPage,
                          TeamPage,
                          Careers,
                          Impact,
                          InstitutionalPartnership,
                          HeroJourneyPage,
                          InstitutionalPartnerProgramPage,
                          CreatorFestPage,
                          PartnersPage,
                          WebinarPage,
                          MathQuizPage,
                          LLPHPage,
                          TutorMarketing,
                          TutorLanding,
                          Subjects,
                          Subject)
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
            NewsIndex,
            PressIndex,
            BookIndex,
            Supporters,
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
            Technology,
            ErrataList,
            PrivacyPolicy,
            PrintOrder,
            ResearchPage,
            TeamPage,
            Careers,
            Impact,
            InstitutionalPartnership,
            HeroJourneyPage,
            InstitutionalPartnerProgramPage,
            CreatorFestPage,
            PartnersPage,
            WebinarPage,
            MathQuizPage,
            LLPHPage,
            TutorMarketing,
            TutorLanding,
            Subjects
        })

class PageTests(WagtailPageTests):
    def setUp(self):
        root_page = Page.objects.get(title="Root")
        self.homepage = HomePage(title="Hello World",
                            slug="hello-world",
                            )
        root_page.add_child(instance=self.homepage)

    def test_can_create_ipp_page(self):
        self.assertCanCreateAt(HomePage, InstitutionalPartnerProgramPage)

    def test_can_create_llph_page(self):
        llph_page = LLPHPage(title="LLPH",
                             heading="Heading",
                             subheading="Subheading",
                             signup_link_href="http://rice.edu",
                             signup_link_text="Click me",
                             info_link_slug="/llph-slug",
                             info_link_text="Click me",
                             book_heading="Book heading",
                             book_description="I should accept <b>HTML</b>.")
        self.homepage.add_child(instance=llph_page)
        self.assertCanCreateAt(HomePage, LLPHPage)

        retrieved_page = Page.objects.get(id=llph_page.id)
        self.assertEqual(retrieved_page.title, "LLPH")

    def test_can_create_team_page(self):
        team_page = TeamPage(title="Team Page",
                             header="Heading",
                             subheader="Subheading",
                             team_header="Our Team")
        self.homepage.add_child(instance=team_page)
        self.assertCanCreateAt(HomePage, TeamPage)
        revision = team_page.save_revision()
        revision.publish()
        team_page.save()

        retrieved_page = Page.objects.get(id=team_page.id)

        self.assertEqual(retrieved_page.title, "Team Page")


class ErrataListTest(WagtailPageTests):

    def test_can_create_errata_list_page(self):
        root_page = Page.objects.get(title="Root")
        homepage = HomePage(title="Hello World",
                            slug="hello-world",
                            )
        root_page.add_child(instance=homepage)
        errata_list_page = ErrataList(title="Errata List Template",
                                      correction_schedule="Some sample correction schedule text.",
                                      new_edition_errata_message="New edition correction text.",
                                      deprecated_errata_message="Deprecated errata message.",
                                      about_header="About our correction schedule.",
                                      about_text="Errata receieved from March through...",
                                      about_popup="Instructor and student resources..."
                                      )
        homepage.add_child(instance=errata_list_page)

        retrieved_page = Page.objects.get(id=errata_list_page.id)
        self.assertEqual(retrieved_page.title, "Errata List Template")


class SubjectsPageTest(WagtailPageTests):

    def test_can_create_subjects_page(self):
        root_page = Page.objects.get(title="Root")
        homepage = HomePage(title="Hello World",
                            slug="hello-world",
                            )
        root_page.add_child(instance=homepage)
        subjects_page = Subjects(title="Subjects",
                                      heading="Testing Subjects Page",
                                      description="This is a Subjects page test",
                                      philanthropic_support="Please support us",
                                      )
        homepage.add_child(instance=subjects_page)

        retrieved_page = Page.objects.get(id=subjects_page.id)
        self.assertEqual(retrieved_page.title, "Subjects")


class SubjectPageTest(WagtailPageTests):

    def test_can_create_subject_page(self):
        root_page = Page.objects.get(title="Root")
        homepage = HomePage(title="Hello World",
                            slug="hello-world",
                            )
        root_page.add_child(instance=homepage)
        subjects_page = Subjects(title="Subjects",
                                      heading="Testing Subjects Page",
                                      description="This is a Subjects page test",
                                      philanthropic_support="Please support us",
                                      )
        homepage.add_child(instance=subjects_page)
        subject_page = Subject(title="Business",
                               page_description="Business page",
                               os_textbook_heading="OpenStax Business Textbooks",
                               philanthropic_support="Please support us",
                               )
        subjects_page.add_child(instance=subject_page)

        retrieved_page = Page.objects.get(id=subject_page.id)
        self.assertEqual(retrieved_page.title, "Business")


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
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sorry, no pages match', response.content)
