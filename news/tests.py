from django.utils import timezone
from django.test import TestCase
from wagtail.tests.utils import WagtailPageTests
from wagtail.core.models import Page
from pages.models import HomePage
from shared.test_utilities import assertPathDoesNotRedirectToTrailingSlash
from unittest.mock import MagicMock
from news.models import NewsIndex, NewsArticle, PressIndex, PressRelease
from news.search import convert_subject_names_to_ids, convert_blog_type_names_to_ids
from snippets.models import Subject, BlogContentType


class NewsTests(WagtailPageTests, TestCase):
    def setUp(self):
        self.math = Subject(name="Math", page_content="Math page content.", seo_title="Math SEO Title",
                            search_description="Math page description.")
        self.math.save()

        self.economics = Subject(name="Economics", page_content="Economics page content.",
                                 seo_title="Economics SEO Title",
                                 search_description="Economics page description.")
        self.economics.save()

        self.case_study = BlogContentType(content_type='Case Study')
        self.case_study.save()

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
        # add book index to homepage
        homepage.add_child(instance=news_index)

        cls.news_index = Page.objects.get(id=news_index.id)

    def test_can_create_news_article(self):
        news_index = NewsIndex.objects.all()[0]
        article = NewsArticle(title="Article 1",
                              slug="article",
                              date=timezone.now(),
                              heading="Sample Article",
                              subheading="Sample Subheading",
                              author="OpenStax")
        news_index.add_child(instance=article)
        self.assertEqual(article.heading, "Sample Article")

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

    def test_convert_subject_names_to_ids_none(self):
        self.assertEqual(convert_subject_names_to_ids(None), [])

    def test_convert_subject_names_to_ids(self):
        converted_ids = convert_subject_names_to_ids(['Math'])
        math_id = Subject.objects.filter(name='Math').first()
        self.assertEqual(math_id.id, converted_ids[0])

    def test_convert_blog_type_names_to_ids_none(self):
        self.assertEqual(convert_blog_type_names_to_ids(None), [])

    def test_convert_blog_type_names_to_ids(self):
        converted_ids = convert_blog_type_names_to_ids(['Case Study'])
        type_id = BlogContentType.objects.filter(content_type='Case Study').first()
        self.assertEqual(type_id.id, converted_ids[0])


# class SearchTest(TestCase):
#     def setUp(self):
#        # create category types
#        # create subjects
#        # create news articles
#
#     def test_search_collection(self):
#         # query data for results
#
#         # call search URL
#
#         # compare results

