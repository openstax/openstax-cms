import datetime
import json

from django.utils import timezone
from django.test import TestCase
from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page
from pages.models import HomePage
from shared.test_utilities import assertPathDoesNotRedirectToTrailingSlash
from unittest.mock import MagicMock
from news.models import NewsIndex, NewsArticle, PressIndex, PressRelease
from snippets.models import Subject, BlogContentType, BlogCollection


class NewsTests(WagtailPageTestCase, TestCase):
    def setUp(self):
        # create collections
        self.learning = BlogCollection(name='Teaching and Learning', description='this is a collection')
        self.learning.save()
        learning_id = self.learning.id

        self.updates = BlogCollection(name='OpenStax Updates', description='this is a collection')
        self.updates.save()
        update_id = self.updates.id
        # create content types
        self.case_study = BlogContentType(content_type='Case Study')
        self.case_study.save()
        case_study_id = self.case_study.id

        self.video = BlogContentType(content_type='Video')
        self.video.save()
        video_id = self.video.id
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
        # create news articles
        news_index = NewsIndex.objects.all()[0]
        self.article = NewsArticle(title="Article 1",
                                   slug="article",
                                   date=timezone.now(),
                                   heading="Sample Article",
                                   subheading="Sample Subheading",
                                   author="OpenStax",
                                   body=json.dumps(
                                       [
                                           {"type": "paragraph",
                                            "value": "<p>This is the body of the post</p><p>This is the second paragraph</p>"}
                                       ]
                                   ),
                                   article_subjects=json.dumps(
                                       [
                                           {'type': 'subject', 'value': [{'type': 'item', 'value': {'subject': math_id, 'featured': False}}]}
                                       ]
                                   ),
                                   content_types=json.dumps(
                                       [
                                           {'type': 'content_type', 'value': [
                                               {'type': 'item', 'value': {'content_type': case_study_id}}]}
                                       ]
                                   ),
                                   collections=json.dumps(
                                       [
                                           {'type': 'collection', 'value': [
                                               {'type': 'item', 'value': {'collection': learning_id, 'featured': False, 'popular': False}}]}
                                       ]
                                   ))
        news_index.add_child(instance=self.article)
        self.article2 = NewsArticle(title="Article 2",
                                    slug="article2",
                                    date=timezone.now(),
                                    heading="Sample Article 2",
                                    subheading="Sample Subheading 2",
                                    author="OpenStax",
                                    body=json.dumps(
                                        [
                                            {"type": "paragraph",
                                             "value": "<p>This is the body of the post</p><p>This is the second paragraph</p>"}
                                        ]
                                    ),
                                    article_subjects=json.dumps(
                                        [
                                            {'type': 'subject', 'value': [{'type': 'item', 'value': {'subject': economics_id, 'featured': False}}]}
                                        ]
                                    ),
                                    content_types=json.dumps(
                                        [
                                            {'type': 'content_type', 'value': [
                                                {'type': 'item', 'value': {'content_type': video_id}}]}
                                        ]
                                    ),
                                    collections=json.dumps(
                                        [
                                            {'type': 'collection', 'value': [
                                                {'type': 'item', 'value': {'collection': update_id, 'featured': False,
                                                                           'popular': False}}]}
                                        ]
                                    ))
        news_index.add_child(instance=self.article2)
        self.article3 = NewsArticle(title="Article 3",
                                    slug="article3",
                                    date=timezone.now(),
                                    heading="Sample Article 3",
                                    subheading="Sample Subheading 3",
                                    author="OpenStax",
                                    body=json.dumps(
                                        [
                                            {"type": "paragraph",
                                             "value": "<p>This is the body of the post</p><p>This is the second paragraph</p>"}
                                        ]
                                    ),
                                    article_subjects=json.dumps(
                                        [
                                            {'type': 'subject', 'value': [{'type': 'item','value': {'subject': math_id,'featured': False}}]}
                                        ]
                                    ),
                                    content_types=json.dumps(
                                        [
                                            {'type': 'content_type', 'value': [
                                                {'type': 'item', 'value': {'content_type': case_study_id}}]}
                                        ]
                                    ),
                                    collections=json.dumps(
                                        [
                                            {'type': 'collection', 'value': [
                                                {'type': 'item', 'value': {'collection': update_id, 'featured': False,
                                                                           'popular': False}}]}

                                        ]
                                    ))
        news_index.add_child(instance=self.article3)
        self.article4 = NewsArticle(title="Article 4",
                                    slug="article4",
                                    date=timezone.now(),
                                    heading="Sample Article 4",
                                    subheading="Sample Subheading 4",
                                    author="OpenStax",
                                    body=json.dumps(
                                        [
                                            {"type": "paragraph",
                                             "value": "<p>This is the body of the post</p><p>This is the second paragraph</p>"}
                                        ]
                                    ),
                                    article_subjects=json.dumps(
                                        [
                                            {'type': 'subject', 'value': [
                                                {'type': 'item', 'value': {'subject': math_id, 'featured': False}}]}
                                        ]
                                    ),
                                    content_types=json.dumps(
                                        [
                                            {'type': 'content_type', 'value': [
                                                {'type': 'item', 'value': {'content_type': case_study_id}}]}
                                        ]
                                    ),
                                    collections=json.dumps(
                                        [
                                            {'type': 'collection', 'value': [
                                                {'type': 'item', 'value': {'collection': update_id, 'featured': False,
                                                                           'popular': False}}]}

                                        ]
                                    ),
                                    live=False)
        news_index.add_child(instance=self.article4)

    @classmethod
    def setUpTestData(cls):
        # create root page
        root_page = Page.objects.get(title="Root")
        # create homepage
        homepage = HomePage(title="Hello World",
                            slug="hello-world",
                            )
        # add homepage to root page
        root_page.add_child(instance=homepage)
        # create book index page
        news_index = NewsIndex(title="News Index")

        homepage.add_child(instance=news_index)

        cls.news_index = Page.objects.get(id=news_index.id)

    def test_bad_slug_returns_404(self):
        response = self.client.get('/apps/cms/api/news/bad-slug/', format='json')
        self.assertEqual(response.status_code, 404)

    def test_slashless_apis_are_good(self):
        NewsIndex.objects.all = MagicMock(return_value=MagicMock(pk=3))
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/news')

        PressIndex.objects.all = MagicMock(return_value=MagicMock(pk=3))
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/press')

        NewsArticle.objects.get = MagicMock(return_value=MagicMock(pk=3))
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/news/slug')

        PressRelease.objects.get = MagicMock(return_value=MagicMock(pk=3))
        assertPathDoesNotRedirectToTrailingSlash(self, '/apps/cms/api/press/slug')

    def test_search_subject_only(self):
        response = self.client.get('/apps/cms/api/search/',{'subjects': 'Math'})
        self.assertContains(response, 'Math')

    def test_search_live_subject_only(self):
        response = self.client.get('/apps/cms/api/search/',{'subjects': 'Math'})
        self.assertNotContains(response, 'Article 4')

    def test_search_blog_collection(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates'})
        self.assertContains(response, 'OpenStax Updates')

    def test_search_live_blog_collection(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates'})
        self.assertNotContains(response, 'Article 4')

    def test_search_blog_content_type(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'types': 'Video'})
        self.assertContains(response, 'OpenStax Updates')
        self.assertContains(response, 'Video')

    def test_search_live_blog_content_type(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'types': 'Case Study'})
        self.assertNotContains(response, 'Article 4')

    def test_search_blogcollection_and_subject(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'subjects': 'Economics'})
        self.assertContains(response, 'OpenStax Updates')
        self.assertContains(response, 'Economics')

    def test_search_blog_content_type_and_subject(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'types': 'Case Study', 'subjects': 'Economics'})
        self.assertContains(response, 'OpenStax Updates')
        self.assertContains(response, 'Case Study')
        self.assertContains(response, 'Economics')

    def test_search_blog_multiple_content_type_and_subject(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'types': 'Case Study,Video', 'subjects': 'Economics,Math'})
        self.assertContains(response, 'OpenStax Updates')
        self.assertContains(response, 'Case Study')
        self.assertContains(response, 'Economics')

    def test_search_two_blog_content_types(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'types': 'Video,Case Study'})
        self.assertContains(response, 'Video')
        self.assertContains(response, 'Case Study')

    def test_search_blog_collection_and_two_subjects(self):
        response = self.client.get('/apps/cms/api/search/', {'collection': 'OpenStax Updates', 'subjects': 'Economics,Math'})
        self.assertContains(response, 'Economics')
        self.assertContains(response, 'Math')


class PressTests(WagtailPageTestCase):
    def setUp(self):
        press_index = PressIndex.objects.all()[0]
        self.press_release = PressRelease(title='Press release',
                                     date=datetime.datetime.now(),
                                     author='someone',
                                     heading='heading',
                                     excerpt='this is a press release',
                                     slug='press-release-1',
                                     path=' ',
                                     depth=1,
                                     body=json.dumps(
                                         [{"id": "ae6f048b-6eb5-42e7-844f-cfcd459f81b5", "type": "heading",
                                           "value": "Press release"},
                                          {"id": "a21bcbd4-fec4-432e-bf06-966d739c6de9", "type": "paragraph",
                                           "value": "<p data-block-key=\"wr6bg\">This is a test of a press release.</p><p data-block-key=\"d57h\">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>"},
                                          {"id": "4d339739-131c-4547-954b-0787afdc4914", "type": "tagline",
                                           "value": "This is a test"}]
                                     )
                                     )
        press_index.add_child(instance=self.press_release)

    @classmethod
    def setUpTestData(cls):
        root_page = Page.objects.get(title="Root")
        homepage = HomePage(title="Hello World", slug="hello-world")
        root_page.add_child(instance=homepage)

        press_index = PressIndex(about='About press index',
                                 press_inquiry_phone='111-111-1111',
                                 press_inquiry_email='press@example.com',
                                 experts_heading='experts heading',
                                 experts_blurb='experts blurb',
                                 infographic_text='infographic text',
                                 title='Press Index',
                                 path=' ',
                                 slug='press',
                                 depth=1)
        # add book index to homepage
        homepage.add_child(instance=press_index)
        cls.press_index = Page.objects.get(id=press_index.id)

    def test_can_create_press_release(self):
        self.assertEqual(self.press_release.title, 'Press release')






