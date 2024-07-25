import datetime
import json
from .functions import remove_locked_links_detail, remove_locked_links_listing, build_document_url, build_image_url

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from wagtail.models import Page
from pages.models import HomePage, RootPage
from books.models import BookIndex, Book
from news.models import NewsIndex, NewsArticle
from snippets.models import Subject, BlogContentType, BlogCollection
from wagtail.documents.models import Document


class TestClass(object):
    pass

class FunctionsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_remove_locked_links_detail(self):
        response = TestClass()
        setattr(response, 'data', {
            'book_faculty_resources': [
                {
                    'link_document_url': 'test',
                    'link_external': 'test',
                    'resource_unlocked': False,
                    'anotherstuff': 'test'
                },
                {
                    'link_document_url': 'test',
                    'link_external': 'test',
                    'resource_unlocked': True,
                    'anotherstuff': 'test'
                }
            ]
        })
        
        remove_locked_links_detail(response)

        self.assertEqual(response.data['book_faculty_resources'][0]["link_document_url"], "")
        self.assertEqual(response.data['book_faculty_resources'][0]["link_external"], "")
        self.assertEqual(response.data['book_faculty_resources'][0]["anotherstuff"], "test")

        self.assertEqual(response.data['book_faculty_resources'][1]["link_document_url"], "test")
        self.assertEqual(response.data['book_faculty_resources'][1]["link_external"], "test")
        self.assertEqual(response.data['book_faculty_resources'][1]["anotherstuff"], "test")

    def test_remove_locked_links_listing(self):
        response = TestClass()
        setattr(response, 'data', {
            'items' : [
                {
                    'book_faculty_resources': [
                        {
                            'link_document_url': 'test',
                            'link_external': 'test',
                            'resource_unlocked': False,
                            'anotherstuff': 'test'
                        },
                        {
                            'link_document_url': 'test',
                            'link_external': 'test',
                            'resource_unlocked': True,
                            'anotherstuff': 'test'
                        }
                    ]
                }
            ]
        })
        
        remove_locked_links_listing(response)

        self.assertEqual(response.data['items'][0]['book_faculty_resources'][0]["link_document_url"], "")
        self.assertEqual(response.data['items'][0]['book_faculty_resources'][0]["link_external"], "")
        self.assertEqual(response.data['items'][0]['book_faculty_resources'][0]["anotherstuff"], "test")

        self.assertEqual(response.data['items'][0]['book_faculty_resources'][1]["link_document_url"], "test")
        self.assertEqual(response.data['items'][0]['book_faculty_resources'][1]["link_external"], "test")
        self.assertEqual(response.data['items'][0]['book_faculty_resources'][1]["anotherstuff"], "test")

    def test_build_document_url(self):
        self.assertIn("test/document.pdf", build_document_url("test/test/document.pdf"))

    def test_build_document_url_none(self):
        self.assertEqual(build_document_url(None), None)

    def test_build_image_url_none(self):
        self.assertEqual(build_image_url(None), None)


class TestOpenGraphMiddleware(TestCase):
    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='twitterbot')
        self.root_page = Page.objects.get(title="Root")
        self.homepage = RootPage(title="Hello World",
                            slug="openstax-homepage",
                            seo_title='OpenStax Home',
                            search_description='Home page for OpenStax'
                            )
        self.root_page.add_child(instance=self.homepage)

    def test_home_page_link_preview(self):
        response = self.client.get('/')
        self.assertContains(response, 'og:image')


    def test_book_link_preview(self):
        test_image = SimpleUploadedFile(name='openstax.png',
                                        content=open("pages/static/images/openstax.png", 'rb').read())
        self.test_doc = Document.objects.create(title='Test Doc', file=test_image)
        book_index = BookIndex(title="Book Index",
                               page_description="Test",
                               dev_standard_1_description="Test",
                               dev_standard_2_description="Test",
                               dev_standard_3_description="Test",
                               dev_standard_4_description="Test",
                               )
        # add book index to homepage
        self.homepage.add_child(instance=book_index)
        book = Book(title="Biology 2e",
                    slug="biology-2e",
                    cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                    description="Test Book",
                    cover=self.test_doc,
                    title_image=self.test_doc,
                    publish_date=datetime.date.today(),
                    locale=self.root_page.locale,
                    license_name='Creative Commons Attribution License',
                    seo_title='Biology 2e',
                    search_description='2nd edition of Biology'
                    )
        book_index.add_child(instance=book)
        self.client = Client(HTTP_USER_AGENT='Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)')
        response = self.client.get('/details/books/biology-2e/')
        self.assertContains(response, 'og:image')

    def test_blog_link_preview(self):
        self.news_index = NewsIndex(title="News Index")
        self.homepage.add_child(instance=self.news_index)
        self.math = Subject(name="Math", page_content="Math page content.", seo_title="Math SEO Title",
                            search_description="Math page description.")
        self.math.save()
        math_id = self.math.id
        self.case_study = BlogContentType(content_type='Case Study')
        self.case_study.save()
        case_study_id = self.case_study.id
        self.learning = BlogCollection(name='Teaching and Learning', description='this is a collection')
        self.learning.save()
        learning_id = self.learning.id
        self.article = NewsArticle(title="Article 1",
                                   slug="article-1",
                                   date=datetime.date.today(),
                                   heading="Sample Article",
                                   subheading="Sample Subheading",
                                   author="OpenStax",
                                   seo_title='Test Article 1',
                                   search_description='Test Article 1 description',
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
                                               {'type': 'item', 'value': {'collection': learning_id, 'featured': False,
                                                                          'popular': False}}]}
                                       ]
                                   ))
        self.news_index.add_child(instance=self.article)
        self.client = Client(HTTP_USER_AGENT='facebookexternalhit/1.1')
        response = self.client.get('/blog/article-1/')
        self.assertContains(response, 'og:image')

