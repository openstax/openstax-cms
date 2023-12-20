import json

from django.test import TestCase
from django.utils import timezone
from wagtail.test.utils import WagtailPageTestCase

from snippets.models import Subject, WebinarCollection
from webinars.models import Webinar


class WebinarTests(WagtailPageTestCase, TestCase):
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

        self.research = WebinarCollection(name="Research", description="this is a description",
                                 image=None)
        self.research.save()
        research_id = self.research.id

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
                               webinar_collections=json.dumps(
                                   [
                                       {"type": "collection", "value": [
                                        {"id": "0e8074ca-5cb6-4637-9411-8c5e20776a04", "type": "item",
                                        "value": {"popular": False, "featured": False, "collection": research_id}
                                         }
                                       ]}
                                   ]
                               ),
                               )
        self.webinar2.save()

    def test_search_subject_only(self):
        response = self.client.get('/apps/cms/api/webinars/?subject=Math')
        self.assertContains(response, 'Math')

    def test_search_collection_only(self):
        response = self.client.get('/apps/cms/api/webinars/?collection=Research')
        self.assertContains(response, 'Research')

    def test_all_webinars(self):
        response = self.client.get('/apps/cms/api/webinars/')
        self.assertContains(response, 'Math')
        self.assertContains(response, 'Economics')

    def test_webinar_search(self):
        response = self.client.get('/apps/cms/api/webinars/search/?q=Webinar 2')
        self.assertContains(response, 'Economics')
        self.assertContains(response, 'Research')
