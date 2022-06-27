import json

from django.test import TestCase
from django.utils import timezone
from wagtail.tests.utils import WagtailPageTests

from snippets.models import Subject
from webinars.models import Webinar


class WebinarTests(WagtailPageTests, TestCase):
    def setUp(self):
        # create subjects
        self.math = Subject(name="Math", page_content="Math page content.", seo_title="Math SEO Title",
                            search_description="Math page description.")
        self.math.save()
        math_id = self.math.id

        self.economics = Subject(name="Economics", page_content="Economics page content.",
                                 seo_title="Economics SEO Title",
                                 search_description="Economics page description.")
        self.economics.save()
        economics_id = self.economics.id

        # create webinars
        self.webinar = Webinar(title="Webinar 1",
                                   start=timezone.now(),
                                   end=timezone.now(),
                                   description='Webinar 1 description',
                                   speakers='Bob, Mary. Sally, Mike',
                                   spaces_remaining=45,
                                   registration_url='https://example.com',
                                   registration_link_text='Register Now',
                                   display_on_tutor_page=False,
                                   webinar_subjects=json.dumps(
                                       [

                                           {"type": "subject", "value": [
                                               {"type": "item", "value": {"subject": math_id, "featured": False},
                                                "id": "fb443e9a-5487-4b5e-86f3-69017c0327b5"}]
                                            }
                                       ]
                                   ),
                                   )
        self.webinar.save()
        self.webinar2 = Webinar(title="Webinar 2",
                               start=timezone.now(),
                               end=timezone.now(),
                               description='Webinar 2 description',
                               speakers='Stan, Steve, Tony',
                               spaces_remaining=54,
                               registration_url='https://example.com',
                               registration_link_text='Register Now',
                               display_on_tutor_page=False,
                               webinar_subjects=json.dumps(
                                   [

                                       {"type": "subject", "value": [
                                           {"type": "item", "value": {"subject": economics_id, "featured": False},
                                            "id": "fb443e9a-5487-4b5e-86f3-69017c0327b5"}]
                                        }
                                   ]
                               ),
                               )
        self.webinar2.save()

    def test_search_subject_only(self):
        response = self.client.get('/apps/cms/api/webinars/?subject=Math')
        self.assertContains(response, 'Math')
