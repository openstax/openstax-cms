import json
from django.test import TestCase, Client

from wagtail.tests.utils import WagtailTestUtils
from wagtail.images.tests.utils import Image, get_test_image_file
from wagtail.documents.models import Document

from shared.test_utilities import assertPathDoesNotRedirectToTrailingSlash

class PagesAPI(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_api_v2_pages_urls(self):
        #make sure we get a 200 with or without a slash, no 3xx
        response = self.client.get('/apps/cms/api/v2/pages/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/apps/cms/api/v2/pages')
        self.assertEqual(response.status_code, 200)


class ImageAPI(TestCase, WagtailTestUtils):

    def setUp(self):
        self.login()

    def test_api_v2_no_images(self):
        response = self.client.get('/apps/cms/api/v2/images/')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'], 0)
        self.assertEqual(response_dict['items'], [])

    def test_api_v2_single_image(self):
        response = self.client.get('/apps/cms/api/v2/images/')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'], 0)
        self.assertEqual(response_dict['items'], [])

        expected_title = "Test image"
        image = Image.objects.create(
            title=expected_title,
            file=get_test_image_file(),
        )

        response = self.client.get('/apps/cms/api/v2/images/')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'], 1)
        returned_title = response_dict['items'][0]['title']
        self.assertEqual(expected_title, returned_title)


class DocumentAPI(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_api_v2_single_document(self):
        response = self.client.get('/apps/cms/api/v2/documents/')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'], 0)
        self.assertEqual(response_dict['items'], [])

        expected_title = "Test document"
        image = Document.objects.create(
            title=expected_title,
            file=get_test_image_file(),
        )

        response = self.client.get('/apps/cms/api/v2/documents/')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'], 1)
        returned_title = response_dict['items'][0]['title']
        self.assertEqual(expected_title, returned_title)

    def test_can_search_documents(self):
        image = Document.objects.create(
            title="OpenStax",
            file=get_test_image_file(),
        )

        response = self.client.get('/apps/cms/api/v2/documents/?search=OpenStax')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'], 1)


class APITests(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()
        self.client = Client()

    def test_footer_api(self):
        response = self.client.get('/apps/cms/api/footer/')
        self.assertEqual(response.status_code, 200)

    def test_school_api(self):
        response = self.client.get('/apps/cms/api/schools/')
        self.assertEqual(response.status_code, 200)

    def test_mapbox_api(self):
        response = self.client.get('/apps/cms/api/mapbox/')
        self.assertEqual(response.status_code, 200)
    
    def test_flags_api(self):
        response = self.client.get('/apps/cms/api/flags/')
        self.assertEqual(response.status_code, 200)

    def test_can_submit_customization_form(self):
        data = {'email': 'test@rice.edu',
                'num_students': 45,
                'reason': 'I want to make a new book',
                'modules': ['1-1-example', '2-2-example']}
        response = self.client.post('/apps/cms/api/customize/',
                                json.dumps(data),
                                content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_bad_submission_returns_400(self):
        data = {'bad-key': 'no-data'}
        response = self.client.post('/apps/cms/api/customize/',
                                    json.dumps(data),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_get_request_returns_nothing(self):
        response = self.client.get('/apps/cms/api/customize/')
        self.assertIn("Only post requests valid for this endpoint", response.content.decode("utf-8"))

    def test_give_today_api(self):
        response = self.client.get('/apps/cms/api/give-today/')
        self.assertEqual(response.status_code, 200)

    def test_sticky_api(self):
        response = self.client.get('/apps/cms/api/sticky/')
        self.assertEqual(response.status_code, 200)
