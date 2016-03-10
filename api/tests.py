from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils
from wagtail.wagtailimages.tests.utils import Image, get_test_image_file


class ImageAPI(TestCase, WagtailTestUtils):

    def setUp(self):
        self.login()
    def target(self,link):
        response = self.client.get(link,follow=True,secure=True)
        self.assertEqual(response.status_code, 200)
        return eval(response.content.decode(response.charset))

    def test_api_v0_no_images(self):
        response_list=self.target('/api/v0/images/')
        self.assertIsInstance(response_list, list)
        self.assertEqual(response_list, [])

    def test_api_v1_no_images(self):
        response_dict=self.target('/api/v1/images/') 
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'], 0)
        self.assertEqual(response_dict['images'], [])

    def test_api_v0_single_image(self):
        expected_title = "Test image"
        image = Image.objects.create(
            title=expected_title,
            file=get_test_image_file(),
        )
        response_list=self.target('/api/v0/images/')

        self.assertIsInstance(response_list, list)
        returned_title = response_list[0]['title']
        self.assertEqual(expected_title, returned_title)
        returned_file_url = response_list[0]['file']
        expected_file_name = image.file.name
        self.assertIn(expected_file_name, returned_file_url)

    def test_api_v1_single_image(self):
        expected_title = "Test image"
        image = Image.objects.create(
            title=expected_title,
            file=get_test_image_file(),
        )
        response_dict=self.target('/api/v1/images/')
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'], 1)
        returned_title = response_dict['images'][0]['title']
        self.assertEqual(expected_title, returned_title)


