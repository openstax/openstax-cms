import json
from django.test import TestCase
from django.urls import reverse
from wagtail.test.utils import WagtailTestUtils
from wagtail.images.tests.utils import Image, get_test_image_file
from wagtail.documents.tests.utils import get_test_document_file
from wagtail.documents.models import Document

from api.models import FeatureFlag, WebviewSettings

from shared.test_utilities import mock_user_login


class PagesAPI(TestCase, WagtailTestUtils):
    def setUp(self):
        pass

    def test_api_v2_pages_urls(self):
        # make sure we get a 200 with or without a slash, no 3xx
        response = self.client.get('/apps/cms/api/v2/pages/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/apps/cms/api/v2/pages', follow=True)
        self.assertEqual(response.status_code, 200)


class ImageAPI(TestCase, WagtailTestUtils):

    def setUp(self):
        pass

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
        pass

    def test_api_v2_single_document(self):
        # Get the URL dynamically
        url = reverse('document-list')  # Update with the actual view name if different

        # Initial GET: Expect empty list
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_dict = response.json()
        self.assertEqual(len(response_dict), 0)
        self.assertEqual(response_dict, [])

        # Create a document
        expected_title = "Test document"
        Document.objects.create(
            title=expected_title,
            file=get_test_document_file(),
        )

        # Second GET: Expect one document
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_dict = response.json()

        # Assertions
        self.assertEqual(len(response_dict), 1)
        self.assertEqual(response_dict[0]['title'], expected_title)

    def test_can_search_documents(self):
        url = reverse('document-list')

        document = Document.objects.create(
            title="OpenStax",
            file=get_test_document_file(),
        )
        self.assertEqual(document.title, 'OpenStax')

        response = self.client.get(url, {'search': 'OpenStax'})
        self.assertEqual(response.status_code, 200)

        # Safer JSON parsing
        response_dict = response.json()

        # Assertions
        self.assertEqual(len(response_dict), 1)
        self.assertEqual(response_dict[0]['title'], 'OpenStax')


class APITests(TestCase, WagtailTestUtils):
    def setUp(self):
        mock_user_login()

    def test_footer_api(self):
        response = self.client.get('/apps/cms/api/footer/')
        self.assertEqual(response.status_code, 200)

    def test_school_api(self):
        response = self.client.get('/apps/cms/api/schools/')
        self.assertEqual(response.status_code, 200)

    def test_mapbox_api(self):
        response = self.client.get('/apps/cms/api/mapbox/')
        self.assertEqual(response.status_code, 200)
    
    def test_can_create_flag(self):
        flag = FeatureFlag.objects.create(name='test_flag', feature_active=True)
        self.assertEqual(FeatureFlag.objects.all().count(), 1)
        self.assertEqual(FeatureFlag.objects.first().name, 'test_flag')
        self.assertEqual(FeatureFlag.objects.first().feature_active, True)

    def test_flags_api(self):
        response = self.client.get('/apps/cms/api/flags/')
        self.assertEqual(response.status_code, 200)

    def test_flags_api_one_result(self):
        flag = FeatureFlag.objects.create(name='super_feature', feature_active=True)
        response = self.client.get('/apps/cms/api/flags/?flag=super_feature')
        self.assertEqual(response.status_code, 200)
        self.assertIn("\"name\": \"super_feature\"", response.content.decode("utf-8"))
        self.assertIn("\"feature_active\": true", response.content.decode("utf-8"))

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

    def test_errata_resource_api(self):
        response = self.client.get('/apps/cms/api/errata-fields/?field=resources')
        self.assertNotIn('content', 'OpenStax Concept Coach')
        self.assertNotIn('content', 'Rover by OpenStax')
        self.assertEqual(response.status_code, 200)

    def test_webview_settings_api(self):
        wvs = WebviewSettings.objects.create(name='Test', value='Test value')
        response = self.client.get('/apps/cms/api/webview-settings/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("\"value\": \"Test value\"", response.content.decode("utf-8"))

