import datetime
import json
import unittest
from unittest.mock import patch

from django.test import TestCase, Client
from wagtail.test.utils import WagtailTestUtils, WagtailPageTestCase
from wagtail.models import Page
from pages import models as page_models

from shared.test_utilities import mock_user_login
from http import cookies

class TestRootPage(unittest.TestCase):

    @patch('pages.models.RootPage.get_url_parts')
    def get_url_parts_returns_correct_values(self, mock_get_url_parts):
        mock_get_url_parts.return_value = (1, 'http://openstax.org', 'some/path')
        root_page = page_models.RootPage()
        result = root_page.get_url_parts()
        self.assertEqual(result, (1, 'http://openstax.org', ''))

    @patch('pages.models.RootPage.get_url_parts')
    def get_url_parts_returns_none_when_no_url_parts(self, mock_get_url_parts):
        mock_get_url_parts.return_value = None
        root_page = page_models.RootPage()
        result = root_page.get_url_parts()
        self.assertIsNone(result)

class HomePageTests(WagtailPageTestCase):

    def setUp(self):
        mock_user_login()

    def test_cant_create_homepage_under_homepage(self):
        self.assertCanNotCreateAt(page_models.HomePage, page_models.HomePage)

    def test_homepage_return_correct_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_can_create_homepage(self):
        root_page = Page.objects.get(title="Root")
        homepage = page_models.HomePage(title="Hello World",
                                        slug="hello-world",
                                        )
        root_page.add_child(instance=homepage)

        retrieved_page = Page.objects.get(id=homepage.id)
        self.assertEqual(retrieved_page.title, "Hello World")


class PageTests(WagtailPageTestCase):
    def setUp(self):
        mock_user_login()
        root_page = Page.objects.get(title="Root")
        self.homepage = page_models.HomePage(title="Hello World",
                                             slug="hello-world",
                                             )
        root_page.add_child(instance=self.homepage)

    def test_can_create_ipp_page(self):
        self.assertCanCreateAt(page_models.HomePage, page_models.InstitutionalPartnerProgramPage)

    def test_can_create_team_page(self):
        team_page = page_models.TeamPage(title="Team Page",
                                         header="Heading",
                                         subheader="Subheading",
                                         team_header="Our Team")
        self.homepage.add_child(instance=team_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.TeamPage)
        revision = team_page.save_revision()
        revision.publish()
        team_page.save()

        retrieved_page = Page.objects.get(id=team_page.id)

        self.assertEqual(retrieved_page.title, "Team Page")

    def test_can_create_about_us_page(self):
        about_us = page_models.AboutUsPage(title='About Us',
                                           who_heading='About Us',
                                           who_paragraph='Who paragraph',
                                           what_heading='what heading',
                                           what_paragraph='what paragraph',
                                           where_heading='where heading',
                                           where_paragraph='where paragraph',
                                           )
        self.homepage.add_child(instance=about_us)
        self.assertCanCreateAt(page_models.HomePage, page_models.AboutUsPage)

        retrieved_page = Page.objects.get(id=about_us.id)
        self.assertEqual(retrieved_page.title, "About Us")

    def test_can_create_k12_main_page(self):
        k12_page = page_models.K12MainPage(title='K12 Main Page',
                                           banner_headline='banner heading',
                                           banner_description='banner description',
                                           subject_list_default='subject list default',
                                           highlights_header='highlights header',
                                           subject_library_header='subjects library header',
                                           subject_library_description='subjects library description',
                                           )
        self.homepage.add_child(instance=k12_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.K12MainPage)

        retrieved_page = Page.objects.get(id=k12_page.id)
        self.assertEqual(retrieved_page.title, "K12 Main Page")

    def test_can_create_contact_us_page(self):
        contact_us_page = page_models.ContactUs(title='Contact Us',
                                                tagline='this is a tagline',
                                                mailing_header='Mailing header',
                                                mailing_address='123 Street, East SomeTown, Tx',
                                                customer_service='How can I help you?',
                                                )
        self.homepage.add_child(instance=contact_us_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.ContactUs)

        retrieved_page = Page.objects.get(id=contact_us_page.id)
        self.assertEqual(retrieved_page.title, "Contact Us")

    def test_can_create_general_page(self):
        general_page = page_models.GeneralPage(title='General Page',
                                               body=json.dumps(
                                                   [{"id": "ae6f048b-6eb5-42e7-844f-cfcd459f81b5", "type": "heading",
                                                     "value": "General Page"},
                                                    {"id": "a21bcbd4-fec4-432e-bf06-966d739c6de9", "type": "paragraph",
                                                     "value": "<p data-block-key=\"wr6bg\">This is a test of a "
                                                              "general page.</p><p data-block-key=\"d57h\">Lorem "
                                                              "ipsum dolor sit amet, consectetur adipiscing elit, "
                                                              "sed do eiusmod tempor incididunt ut labore et dolore "
                                                              "magna aliqua. Ut enim ad minim veniam, quis nostrud "
                                                              "exercitation ullamco laboris nisi ut aliquip ex ea "
                                                              "commodo consequat. Duis aute irure dolor in "
                                                              "reprehenderit in voluptate velit esse cillum dolore eu "
                                                              "fugiat nulla pariatur. Excepteur sint occaecat "
                                                              "cupidatat non proident, sunt in culpa qui officia "
                                                              "deserunt mollit anim id est laborum.</p>"},
                                                    {"id": "4d339739-131c-4547-954b-0787afdc4914", "type": "tagline",
                                                     "value": "This is a test"}]
                                               ),
                                               )
        self.homepage.add_child(instance=general_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.GeneralPage)

        retrieved_page = Page.objects.get(id=general_page.id)
        self.assertEqual(retrieved_page.title, "General Page")

    def test_can_create_supporters_page(self):
        supporters_page = page_models.Supporters(title='Supporters Page',
                                                 banner_heading='Banner heading',
                                                 banner_description='Banner description',
                                                 funder_groups=json.dumps(
                                                     [{"id": "5cf47334-37f6-433c-b695-80936bc7d236", "type": "content",
                                                       "value":
                                                           {"image": None, "funders": [
                                                               {"id": "647ce8be-eabb-40a2-abb9-136c2bb00e53",
                                                                "type": "item", "value": {"url": "https://openstax.org",
                                                                                          "funder_name": "Musser "
                                                                                                         "Foundation"}},
                                                               {"id": "c31a9a7a-f6e2-4b74-929b-5bc39f96568d",
                                                                "type": "item", "value": {"url": "https://openstax.org",
                                                                                          "funder_name": "Mike and "
                                                                                                         "Patricia "
                                                                                                         "Foundation"}}
                                                               ]}}]
                                                 ),
                                                 disclaimer='This field cannot be left blank',
                                                 )
        self.homepage.add_child(instance=supporters_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.Supporters)

        retrieved_page = Page.objects.get(id=supporters_page.id)
        self.assertEqual(retrieved_page.title, "Supporters Page")

    def test_can_create_tos_page(self):
        tos_page = page_models.TermsOfService(title='Terms of Service Page',
                                              intro_heading='Intro heading',
                                              terms_of_service_content='This is the terms of service',
                                              )
        self.homepage.add_child(instance=tos_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.TermsOfService)

        retrieved_page = Page.objects.get(id=tos_page.id)
        self.assertEqual(retrieved_page.title, "Terms of Service Page")

    def test_can_create_faq_page(self):
        faq_page = page_models.FAQ(title='FAQ Page',
                                   intro_heading='Intro heading',
                                   intro_description='This is the FAQ page',
                                   questions=json.dumps(
                                       [{"id": "bc328439-9ad5-4fe7-9adc-1dba59389330", "type": "question",
                                         "value": {"slug": "how-does-openstax-work",
                                                   "answer": "<p>Using OpenStax is simple! Review the textbook "
                                                             "online, and if you decide to use it in your class, "
                                                             "<a href=\"https://openstax.org/adoption\">let us "
                                                             "know</a>. To access faculty-only materials, "
                                                             "you can create an OpenStax account and request faculty "
                                                             "access. Once we manually verify that you’re an "
                                                             "instructor, you will have access to all faculty "
                                                             "content. Include the textbook URL in your course "
                                                             "materials, and from there, students can choose how they "
                                                             "want to view the book.</p><p>If you’re a student, "
                                                             "simply access the web view, download a PDF, or purchase "
                                                             "a hard copy via Amazon or your campus. Even students "
                                                             "whose professors have not adopted OpenStax are welcome "
                                                             "to use OpenStax textbooks.<br/></p>",
                                                   "document": None, "question": "<p>How does OpenStax work?</p>"}},
                                        {"id": "c985605f-cc41-4758-84dc-a5e42098814c", "type": "question",
                                         "value": {"slug": "why-use-openstax-textbooks",
                                                   "answer": "<p>The costs of textbooks are rising, and students have "
                                                             "difficulty keeping up with the high price of required "
                                                             "materials. A large percentage of students show up for "
                                                             "the first day of class without the course textbook. "
                                                             "Imagine if every student had immediate, "
                                                             "unlimited access to the text. How would that help you "
                                                             "meet your goals?</p><p>Open resources also allow you to "
                                                             "use the text in a way that’s best for you and your "
                                                             "students. You aren’t bound by copyright or digital "
                                                             "rights restrictions, and you can adapt the book as you "
                                                             "see fit.</p>",
                                                   "document": None,
                                                   "question": "<p>Why should instructors use OpenStax "
                                                               "textbooks?<br/></p>"}}
                                        ]
                                   )
                                   )
        self.homepage.add_child(instance=faq_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.FAQ)

        retrieved_page = Page.objects.get(id=faq_page.id)
        self.assertEqual(retrieved_page.title, "FAQ Page")

    def test_can_create_accessibility_page(self):
        accessibility_page = page_models.Accessibility(title='Accessibility Page',
                                                       intro_heading='Intro heading',
                                                       accessibility_content='This is about accessibility',
                                                       )
        self.homepage.add_child(instance=accessibility_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.Accessibility)

        retrieved_page = Page.objects.get(id=accessibility_page.id)
        self.assertEqual(retrieved_page.title, "Accessibility Page")

    def test_can_create_licensing_page(self):
        licensing_page = page_models.Licensing(title='Licensing Page',
                                               intro_heading='Intro heading',
                                               licensing_content='This is about licensing',
                                               )
        self.homepage.add_child(instance=licensing_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.Licensing)

        retrieved_page = Page.objects.get(id=licensing_page.id)
        self.assertEqual(retrieved_page.title, "Licensing Page")

    def test_can_create_technology_page(self):
        technology_page = page_models.Technology(title='Technology Page',
                                                 intro_heading='Intro heading',
                                                 intro_description='intro description',
                                                 banner_cta='CTA!, CTA!',
                                                 select_tech_heading='select tech heading',
                                                 select_tech_step_1='Step 1',
                                                 select_tech_step_2='Step 2',
                                                 select_tech_step_3='Step 3',
                                                 new_frontier_heading='new frontier heading',
                                                 new_frontier_subheading='subheading',
                                                 new_frontier_description='new frontier description',
                                                 new_frontier_cta_1='CTA 1',
                                                 new_frontier_cta_2='CTA 2',
                                                 )
        self.homepage.add_child(instance=technology_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.Technology)

        retrieved_page = Page.objects.get(id=technology_page.id)
        self.assertEqual(retrieved_page.title, "Technology Page")

    def test_can_create_careers_page(self):
        careers_page = page_models.Careers(title='Careers Page',
                                           intro_heading='Intro heading',
                                           careers_content='This is about careers',
                                           )
        self.homepage.add_child(instance=careers_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.Careers)

        retrieved_page = Page.objects.get(id=careers_page.id)
        self.assertEqual(retrieved_page.title, "Careers Page")

    def test_can_create_privacy_policy_page(self):
        privacy_page = page_models.PrivacyPolicy(title='Privacy Policy Page',
                                                 intro_heading='Intro heading',
                                                 privacy_content='This is about privacy',
                                                 )
        self.homepage.add_child(instance=privacy_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.PrivacyPolicy)

        retrieved_page = Page.objects.get(id=privacy_page.id)
        self.assertEqual(retrieved_page.title, "Privacy Policy Page")

    def test_can_create_impact_page(self):
        impact_page = page_models.Impact(title='Impact Page',
                                         improving_access=json.dumps(
                                             [{"id": "b42f66a2-a4b2-4c84-a581-3535a0fbc20b", "type": "content",
                                               "value": {"image": {"link": "", "image": None},
                                                         "heading": "Why Open Education Matters",
                                                         "button_href": "https://riceconnect.rice.edu/donation"
                                                                        "/support-openstax-impact",
                                                         "button_text": "Give today",
                                                         "description": "<p data-block-key=\"zmm6z\">OpenStax "
                                                                        "believes that learning is a public good and "
                                                                        "that every learner has the fundamental right "
                                                                        "to pursue their education in areas that "
                                                                        "inspire them most. Our goal is to remain "
                                                                        "100% free and easily accessible, "
                                                                        "while improving learning proficiency for "
                                                                        "every learner. Open education can open "
                                                                        "doorways to new careers, intellectual "
                                                                        "pursuits, and the betterment of "
                                                                        "society.</p><p data-block-key=\"2066m\">What "
                                                                        "might you achieve if you had the right "
                                                                        "resources at your fingertips? Join us today "
                                                                        "and help millions of learners experience an "
                                                                        "affordable and engaging education.</p><p "
                                                                        "data-block-key=\"6glab\"></p>"}}]
                                         ),
                                         reach=json.dumps(
                                             [{"id": "0b1d5fe8-f77a-4eb6-ae6a-1dc58cb08c10", "type": "content",
                                               "value": {"cards": [
                                                   {"id": "ce31a4fb-b929-493e-96ce-5ea945c82ddd", "type": "item",
                                                    "value": {"icon": None,
                                                              "link_href": "https://openstax.org/press/openstax"
                                                                           "-surpasses-1-billion-textbook-savings-wide-ranging-impact-teaching-learning-and-student-success",
                                                              "link_text": "Read more",
                                                              "description": "$1.8 billion saved in education costs "
                                                                             "since 2012"
                                                              }
                                                    }
                                               ]}}]
                                         ),
                                         quote=json.dumps(
                                             [{"id": "49d89977-5433-4b1f-9e0f-ed4982ac4201", "type": "content",
                                               "value": {"image": {"link": "", "image": None},
                                                         "quote": "<p data-block-key=\"caakp\">I believe that "
                                                                  "knowledge should be free. And that means we "
                                                                  "shouldn’t be tying up ideas and knowledge in "
                                                                  "proprietary systems. We should be finding ways to "
                                                                  "share ideas and knowledge to make the world a "
                                                                  "better place. <b>– Prof. Richard Baraniuk,"
                                                                  "</b></p><p data-block-key=\"m9bee\">Founder of "
                                                                  "OpenStax, the C. Sidney Burrus Professor "
                                                                  "of Electrical and Computer Engineering at Rice "
                                                                  "University, and Fellow of the American Academy of "
                                                                  "Arts and Sciences</p>"}}]
                                         ),
                                         making_a_difference=json.dumps(
                                             [{"id": "c1dc4294-2b44-4320-9d72-2286af863302", "type": "content",
                                               "value": {"heading": "Community Stories", "stories": [
                                                   {"id": "8593338c-752a-491c-8b07-33ef8d42bc10", "type": "item",
                                                    "value": {"image": None,
                                                              "story_text": "Rahul Kane grew up in India in a family "
                                                                            "of educators, and upon completing his "
                                                                            "undergraduate studies, moved to the "
                                                                            "United States in 2005 to pursue graduate "
                                                                            "school. Now, he teaches biology at "
                                                                            "Century College and the University of "
                                                                            "St. Thomas. Read more about why he "
                                                                            "prefers open educational resources!",
                                                              "linked_story": None, "embedded_video": ""}},
                                                   {"id": "29293e1b-bd9c-4f66-8e7d-d35e279aaee9", "type": "item",
                                                    "value": {"image": None,
                                                              "story_text": "Megan expects to get her nursing diploma "
                                                                            "in five years and sees herself as a "
                                                                            "successful nurse working in a hospital.",
                                                              "linked_story": None, "embedded_video": ""}}]}}]
                                         ),
                                         disruption=json.dumps(
                                             [{"id": "81f78c27-d65b-449a-b930-21a3449c11f1", "type": "content",
                                               "value": {"graph": {"image": {"link": "", "image": None},
                                                                   "image_alt_text": ""},
                                                         "heading": "Positive Disruption",
                                                         "description": "The price of textbooks is declining due to "
                                                                        "open education’s disruption of the college "
                                                                        "textbook market, removing financial barriers "
                                                                        "to advanced education, and reducing student "
                                                                        "debt. According to an economist, "
                                                                        "“The ‘textbook bubble’ is finally starting "
                                                                        "to deflate, due to the creative destruction "
                                                                        "and competition from free/low-cost textbooks "
                                                                        "from groups like OpenStax” (Mark Perry, AEI, "
                                                                        "2019)."}}]
                                         ),
                                         supporter_community=json.dumps(
                                             [{"id": "0d555d88-1c47-483f-bdd7-bd64aa4fae39", "type": "content",
                                               "value": {"image": {"link": "", "image": None},
                                                         "quote": "<p data-block-key=\"p94bw\">OpenStax continues to "
                                                                  "expand to new subject areas, grade levels, "
                                                                  "and languages to reach more students. Yet, "
                                                                  "OpenStax is more than free textbooks. With a team "
                                                                  "of researchers, educators, and learning engineers "
                                                                  "at Rice University, OpenStax is creating "
                                                                  "research-based learning tools to help teachers and "
                                                                  "learners better personalize the education "
                                                                  "experience. OpenStax needs your partnership to "
                                                                  "continue its impact.</p><p "
                                                                  "data-block-key=\"566uh\"></p><p "
                                                                  "data-block-key=\"67bds\">– <b>Ann Doerr</b>, "
                                                                  "OpenStax Advisor</p>",
                                                         "heading": "Our Supporter Community",
                                                         "link_href": "https://openstax.org/foundation",
                                                         "link_text": "View our supporters"}}]
                                         ),
                                         giving=json.dumps(
                                             [{"id": "e5a9a3ad-f8c6-409f-a774-f6c99daf4990", "type": "content",
                                               "value": {"heading": "Students need your help today.",
                                                         "link_href": "https://example.com/donate",
                                                         "link_text": "Give today",
                                                         "description": "Together, we can increase educational equity "
                                                                        "and quality for millions of students "
                                                                        "worldwide.",
                                                         "nonprofit_statement": "As a part of Rice University, a 501("
                                                                                "c)(3) nonprofit, gifts to OpenStax "
                                                                                "are tax deductible to the fullest "
                                                                                "extent allowed by law. Our tax ID "
                                                                                "number is 00-111111. Read our latest "
                                                                                "Annual Report",
                                                         "annual_report_link_href": "https://example.com/annual-report",
                                                         "annual_report_link_text": "Read our latest OpenStax Brochure"}}]
                                         )

                                         )
        self.homepage.add_child(instance=impact_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.Impact)

        retrieved_page = Page.objects.get(id=impact_page.id)
        self.assertEqual(retrieved_page.title, "Impact Page")

        story_page = page_models.ImpactStory(title='Impact Story Page',
                                             date=datetime.datetime.now(),
                                             heading='Impact Story',
                                             author='Jane Doe',
                                             body=json.dumps(
                                                 [{"id": "ae6f048b-6eb5-42e7-844f-cfcd459f81b5", "type": "heading",
                                                   "value": "Impact Story"}])
                                             )
        impact_page.add_child(instance=story_page)
        self.assertCanCreateAt(page_models.Impact, page_models.ImpactStory)

        retrieved_page = Page.objects.get(id=story_page.id)
        self.assertEqual(retrieved_page.title, "Impact Story Page")

    def test_can_create_learning_research_page(self):
        research_page = page_models.LearningResearchPage(title='Learning Research Page',
                                                         mission_body='This is our mission',
                                                         research_area_header='Research area header',
                                                         research_area_description_mobile='Research area mobile header',
                                                         people_header='People header',
                                                         publication_header='Publication header'
                                                         )
        self.homepage.add_child(instance=research_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.LearningResearchPage)

        retrieved_page = Page.objects.get(id=research_page.id)
        self.assertEqual(retrieved_page.title, "Learning Research Page")

    def test_can_create_webinar_page(self):
        webinar_page = page_models.WebinarPage(title='Webinar Page',
                                               heading='Heading',
                                               )
        self.homepage.add_child(instance=webinar_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.WebinarPage)

        retrieved_page = Page.objects.get(id=webinar_page.id)
        self.assertEqual(retrieved_page.title, "Webinar Page")

    def test_can_create_form_headings_page(self):
        form_page = page_models.FormHeadings(title='Form Headings Page',
                                             adoption_intro_heading='Adoption intro heading',
                                             adoption_intro_description='Adoption intro description',
                                             interest_intro_heading='Interest intro heading',
                                             interest_intro_description='Interest intro description'
                                             )
        self.homepage.add_child(instance=form_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.FormHeadings)

        retrieved_page = Page.objects.get(id=form_page.id)
        self.assertEqual(retrieved_page.title, "Form Headings Page")

    def test_can_create_ally_logos_page(self):
        ally_page = page_models.AllyLogos(title='Ally Logos Page',
                                          heading='Ally logos heading',
                                          description='Alloy logos description',
                                          ally_logos_heading='Ally logos heading',
                                          ally_logos_description='Ally logos description',
                                          ally_logos='',
                                          book_ally_logos_heading='Book ally logo heading',
                                          book_ally_logos_description='Book ally logo description',
                                          book_ally_logos='',
                                          )
        self.homepage.add_child(instance=ally_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.AllyLogos)

        retrieved_page = Page.objects.get(id=ally_page.id)
        self.assertEqual(retrieved_page.title, "Ally Logos Page")

    def test_can_create_assignable_page(self):
        assignable_page = page_models.Assignable(title='Assignable Page',
                                                 subheading='Assignable subheading',
                                                 heading_description='Assignable heading description',
                                                 add_assignable_cta_header='Add assignable heading',
                                                 add_assignable_cta_description='Add assignable description',
                                                 add_assignable_cta_button_text='Add assignable',
                                                 available_courses_header='Available courses header',
                                                 courses_coming_soon_header='Courses coming soon header',
                                                 )
        self.homepage.add_child(instance=assignable_page)
        self.assertCanCreateAt(page_models.HomePage, page_models.Assignable)

        retrieved_page = Page.objects.get(id=assignable_page.id)
        self.assertEqual(retrieved_page.title, "Assignable Page")


class ErrataListTest(WagtailPageTestCase):

    def setUp(self):
        mock_user_login()

    def test_can_create_errata_list_page(self):
        root_page = Page.objects.get(title="Root")
        homepage = page_models.HomePage(title="Hello World",
                                        slug="hello-world",
                                        )
        root_page.add_child(instance=homepage)
        errata_list_page = page_models.ErrataList(title="Errata List Template",
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


class SubjectsPageTest(WagtailPageTestCase):

    def setUp(self):
        mock_user_login()

    def test_can_create_subjects_page(self):
        root_page = Page.objects.get(title="Root")
        homepage = page_models.HomePage(title="Hello World",
                                        slug="hello-world",
                                        )
        root_page.add_child(instance=homepage)
        subjects_page = page_models.Subjects(title="Subjects",
                                             heading="Testing Subjects Page",
                                             description="This is a Subjects page test",
                                             philanthropic_support="Please support us",
                                             )
        homepage.add_child(instance=subjects_page)

        retrieved_page = Page.objects.get(id=subjects_page.id)
        self.assertEqual(retrieved_page.title, "Subjects")


class SubjectPageTest(WagtailPageTestCase):

    def setUp(self):
        mock_user_login()

    def test_can_create_subject_page(self):
        root_page = Page.objects.get(title="Root")
        homepage = page_models.HomePage(title="Hello World",
                                        slug="hello-world",
                                        )
        root_page.add_child(instance=homepage)
        subjects_page = page_models.Subjects(title="Subjects",
                                             heading="Testing Subjects Page",
                                             description="This is a Subjects page test",
                                             philanthropic_support="Please support us",
                                             )
        homepage.add_child(instance=subjects_page)
        subject_page = page_models.Subject(title="Business",
                                           page_description="Business page",
                                           os_textbook_heading="OpenStax Business Textbooks",
                                           philanthropic_support="Please support us",
                                           book_categories_heading="Business book categories",
                                           learn_more_heading="learn more",
                                           learn_more_blog_posts="Business blog posts",
                                           learn_more_webinars="business webinars",
                                           learn_more_about_books="Learn more about our books",
                                           )
        subjects_page.add_child(instance=subject_page)

        retrieved_page = Page.objects.get(id=subject_page.id)
        self.assertEqual(retrieved_page.title, "Business")


class AdminPages(TestCase, WagtailTestUtils):

    def setUp(self):
        self.client = Client()
        self.sso_cookie = 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..mktqRLloaCze0VeT.0WU9d20PI1Iu6zajuQMiIJ5GQJVy0DQ1H3BINxkYIS56f1X6p_mesuujHphLcukQny6q0_rmvZUkKLEyojpo14p3czXXu0GF2EWtxprPmfOnPdAig0GXCBJxYVbxKIuZdR4FYodIZaDuDUjXC_hJohHuVoiTQW7jJEGIFj8m9dgAqP-3hOnqaO0C0OvKWoXi0sLb3CvTraT2AGRgj69jkg4B-2y1sUZn_yZO6o2HekGlxzhnKT7ILEAl7cd68W6LmmN0vk4V4nNFkcg0XQ3i1MzWLZroGSjD_9HrhALdHcofBC39UClOzxnbpynFlZk0gr7m0_MmCUFqWKSL8G0eRT9sgOIW6THsl0jpT4KyUFREVdGkTWxaS2qYRqZEQBk9wZlAHuHkE8s6UNZNYhvU5RJkGC1m4faHnM_umTEFQq5aBvRe7gq_8OtOGASXtmFggapuUSfxWX8Bxh8IgA4BT_DuxQbC4biO7FauOT0glZ0Dk4ZXIjbhxBnedtjmeH02xa4RpcKOSOv4UMy1ajCc4KLp9K5drQTKs1PeShAUg1aN58ZwgQq1w4MdjXHkMqnJFiFWt9abF3WYG2EywhTogxIcgq6IrrAIzW4NSptnQVAcxTPxp7hb3OT1mY9dcK138h0GtBR6Z562VbDRaSwplXCLvwcqKoGJyhotcl2m78ESmu1kIO_AJVstlaZprEA0Ji0A7uJlL03JAeTvlJptcouFGax8LGlxq9Ekpz_zifUxLR52MJ8otKcapsZvmtOpc8A70p7V-ceinzKdL5Jq_zA0teJ1Qk2gjMJ7IdeyG3VZ0QIFOQ_FffGkbdW1Ow-nHFHLVfHbkyEF65HIGHEN_RqL0OKUa1HcPlmL5c1S4w5zgdA-2ZAda6ASnY1clwGufFek5AwMp5SAUmdNUBYIDdQm6hbzn0Xe2VB5Y-jqKBOq4yk-M4rmwAf-tD5NJiKaYLZwT-Zst2eG8InRUOmQt6lBJtGNIYnk_a__rX8rfJpvKIJ-Ws8b9fHvSjzSQOroqM3KmfLrevucaJA7jM7CydgOOnt3VQGXKnYqgnhD6jii0zjR3sGAJHF24tQIVtoFCQGBJZly_MQL2Y-EeLqz64Z7AZDptM9oXK035cbvMMuzG9b1jH3XE2o3gO5ekixDpMwTKT8uI1wH9gOqbf9ehirExYgxEh-EVXTlT6t-kk4N-tu83zCLi8MZNTAVqlisakFlnkn4o53Bj5nn9bRQT61HJG_cLxs.Sz3rB-YyqatRUpekkxpyfw'

    @property
    def target(self):
        def test_redirect(path):
            biscuits = cookies.SimpleCookie()
            biscuits['oxa'] = self.sso_cookie
            self.client.cookies = biscuits
            mock_user_login()

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
