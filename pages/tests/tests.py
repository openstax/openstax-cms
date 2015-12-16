from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils
from wagtail.wagtailimages.tests.utils import Image, get_test_image_file


class TestPages(TestCase, WagtailTestUtils):

    def setUp(self):
        self.login()

    def test_homepage_return_correct_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

class ImageAPI(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def test_api_v0_no_images(self):
        response = self.client.get('/api/v0/images/')
        self.assertEqual(response.status_code, 200)
        response_list = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_list,list)
        self.assertEqual(response_list,[])

    def test_api_v1_no_images(self):
        response = self.client.get('/api/v1/images/')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'],0)
        self.assertEqual(response_dict['images'],[])

    def test_api_v0_single_image(self):
        response = self.client.get('/api/v0/images/')
        self.assertEqual(response.status_code, 200)
        response_list = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_list,list)
        self.assertEqual(response_list,[])

        expected_title = "Test image"
        image = Image.objects.create(
            title=expected_title,
            file=get_test_image_file(),
        )

        response = self.client.get('/api/v0/images/')
        self.assertEqual(response.status_code, 200)
        response_list = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_list,list)
        returned_title = response_list[0]['title']
        self.assertEqual(expected_title,returned_title)
        returned_file_url = response_list[0]['file']
        expected_file_name = image.file.name
        self.assertIn(expected_file_name,returned_file_url)

    def test_api_v1_single_image(self):
        response = self.client.get('/api/v1/images/')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'],0)
        self.assertEqual(response_dict['images'],[])

        expected_title = "Test image"
        image = Image.objects.create(
            title=expected_title,
            file=get_test_image_file(),
        )

        response = self.client.get('/api/v1/images/')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'],1)
        returned_title = response_dict['images'][0]['title']
        self.assertEqual(expected_title,returned_title)
       

class AdminPages(TestCase, WagtailTestUtils):

    def setUp(self):
        self.login()

    @property
    def target(self):
        def test_redirect(path):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 301)
            perm_redirect_url = response.url
            response = self.client.get(perm_redirect_url)
            self.assertEqual(response.status_code, 200)
            return response
        return test_redirect

    def test_admin_link(self):
        self.target('/admin')

    def test_images_link(self):
        self.target('/admin/images')

    def test_pages_link(self):
        self.target('/admin/pages')

    def test_documents_link(self):
        self.target('/admin/documents')

    def test_snippets_link(self):
        self.target('/admin/snippets')

    def test_users_link(self):
        self.target('/admin/users')

    def test_groups_link(self):
        self.target('/admin/groups')

    # A lazy test of our search field without parsing html
    def test_admin_search(self):
        response = self.client.get('/admin/pages/search/?q=openstax')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sorry, no pages match',response.content)

