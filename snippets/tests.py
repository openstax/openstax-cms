import json
from urllib.parse import urlencode
from urllib.request import urlopen

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse

from snippets.models import Subject


class SnippetsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.math = Subject(name="Math", page_content="Math page content.", seo_title="Math SEO Title", search_description="Math page description.")
        self.math.save()

        self.economics = Subject(name="Economics", page_content="Economics page content.", seo_title="Economics SEO Title",
                            search_description="Economics page description.")
        self.economics.save()

    def test_can_create_subject(self):
        subject = Subject(name="Science", page_content="Science page content.", seo_title="Science SEO Title",
                            search_description="Science page description.")
        subject.save()

        self.assertEqual(subject.name, "Science")

    def test_can_fetch_all_subjects(self):
        response = self.client.get('/apps/cms/api/snippets/subjects/?format=json')
        self.assertIn(b"Math SEO Title", response.content)
        self.assertIn(b"Economics page description.", response.content)

    def test_can_query_subjects_by_name(self):
        response = self.client.get('/apps/cms/api/snippets/subjects/?name=Math&format=json')
        self.assertIn(b"Math page content.", response.content)
