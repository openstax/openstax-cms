from .functions import remove_locked_links_detail, remove_locked_links_listing, build_document_url, build_image_url

from django.test import TestCase, Client

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
