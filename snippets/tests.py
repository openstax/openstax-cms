import json
from urllib.parse import urlencode
from urllib.request import urlopen

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse

from snippets.models import Subject, ErrataContent, GiveBanner


class SnippetsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.math = Subject(name="Math", page_content="Math page content.", seo_title="Math SEO Title", search_description="Math page description.")
        self.math.save()

        self.economics = Subject(name="Economics", page_content="Economics page content.", seo_title="Economics SEO Title",
                            search_description="Economics page description.")
        self.economics.save()

        self.live = ErrataContent(heading='Errata Content - Live', book_state='live', content='All OpenStax textbooks undergo a rigorous review process. However, like any professional-grade textbook, errors sometimes occur. The good part is, since our books are web-based, we can make updates periodically. If you have a correction to suggest, submit it here. We review your suggestion and make necessary changes.')
        self.live.save()

        self.deprecated = ErrataContent(heading='Errata Content - Deprecated', book_state='deprecated', content='No more corrections will be made')
        self.deprecated.save()

        self.give_banner = GiveBanner(html_message="Help students around the world succeed with <strong>contributions of $5, $10 or $20</strong>", link_text="Make a difference now", link_url='https://example.com')
        self.give_banner.save()

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

    def test_can_fetch_all_errata_content(self):
        response = self.client.get('/apps/cms/api/snippets/erratacontent/?format=json')
        self.assertIn(b"live", response.content)
        self.assertIn(b"deprecated", response.content)

    def test_can_query_errata_content_by_book_state(self):
        response = self.client.get('/apps/cms/api/snippets/erratacontent/?book_state=deprecated&format=json')
        self.assertIn(b"deprecated", response.content)

    def test_can_fetch_all_give_banners(self):
        response = self.client.get('/apps/cms/api/snippets/givebanner/?format=json')
        self.assertIn(b"Help students", response.content)
