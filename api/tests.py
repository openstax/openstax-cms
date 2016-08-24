import json
import time
import unittest

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import LiveServerTestCase, TestCase
from django.utils.six import StringIO
from wagtail.tests.utils import WagtailPageTests, WagtailTestUtils
from wagtail.wagtailimages.tests.utils import Image, get_test_image_file

from accounts.utils import create_user


class UserAPI(LiveServerTestCase, WagtailPageTests):
    serialized_rollback = True

    def setUp(self):
        super(LiveServerTestCase, self).setUp()
        super(WagtailPageTests, self).setUp()
        [user.delete() for user in User.objects.all()]

    @unittest.skip("SF password expired")
    def test_anonymous_user_fields(self):
        response = self.client.get('/api/user/')
        user_list = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(user_list), 1)
        user_dict = user_list[0]
        returned_set = set(user_dict.keys())
        expected_set = set(
            ['username', 'accounts_id', 'is_superuser', 'groups', 'is_staff'])
        self.assertSetEqual(expected_set, returned_set)

    @unittest.skip("faculty group failing")
    def test_user_faculty_group(self):
        user = User.objects.create_user('john',
                                        'lennon@thebeatles.com',
                                        'johnpassword')
        user.save()
        self.client.force_login(user)
        response = self.client.get('/api/user/')
        self.assertEqual(response.status_code, 200)
        response_list = json.loads(response.content.decode(response.charset))
        expected_user_info = {'is_superuser': False,
                              'username': 'john',
                              'first_name': '',
                              'groups': [],
                              'last_name': '',
                              'is_staff': False,
                              'accounts_id': None}
        returned_user_info = response_list[0]
        self.assertDictEqual(expected_user_info, returned_user_info)

        test_user = {'last_name': 'last_name',
                     'username': 'username',
                     'full_name': None,
                     'first_name': 'first_name',
                     'uid': '0'}

        new_user = create_user(**test_user)

        self.client.force_login(new_user)
        self.client.get('/api/user/')
        time.sleep(1)
        response = self.client.get('/api/user/')
        self.assertEqual(response.status_code, 200)
        response_list = json.loads(response.content.decode(response.charset))
        expected_user_info = {'is_superuser': False,
                              'username': 'username',
                              'first_name': 'first_name',
                              'groups': ['Faculty'],
                              'last_name': 'last_name',
                              'is_staff': False,
                              'accounts_id': '0'}
        returned_user_info = response_list[0]
        self.assertDictEqual(expected_user_info, returned_user_info)

    @unittest.skip("SF password expired")
    def test_adopters(self):
        # Test No adopters
        response = self.client.get('/api/adopters/')
        self.assertEqual(response.status_code, 200)
        response_list = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_list, list)
        self.assertEqual(response_list, [])

        # Test with adopters
        out = StringIO()
        call_command('update_adopters', stdout=out)
        response = self.client.get('/api/adopters/')
        self.assertEqual(response.status_code, 200)
        response_list = json.loads(response.content.decode(response.charset))
        self.assertIsInstance(response_list, list)
        self.assertGreater(len(response_list), 1)
        response_item = response_list[0]
        self.assertIsInstance(response_item, dict)
        expected_set = {'description', 'website', 'name'}
        returned_set = set(response_item.keys())
        self.assertSetEqual(expected_set, returned_set)
        names = [adopter['name'] for adopter in response_list]
        self.assertIn('Rice University', names)

    def tearDown(self):
        super(WagtailPageTests, self).setUp()
        super(LiveServerTestCase, self).setUp()


class ImageAPI(TestCase, WagtailTestUtils):

    def setUp(self):
        self.login()

    def test_api_v0_no_images(self):
        response = self.client.get('/api/images/')
        self.assertEqual(response.status_code, 200)
        response_list = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_list, list)
        self.assertEqual(response_list, [])

    def test_api_v1_no_images(self):
        response = self.client.get('/api/v1/images/')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'], 0)
        self.assertEqual(response_dict['images'], [])

    def test_api_v0_single_image(self):
        response = self.client.get('/api/images/')
        self.assertEqual(response.status_code, 200)
        response_list = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_list, list)
        self.assertEqual(response_list, [])

        expected_title = "Test image"
        image = Image.objects.create(
            title=expected_title,
            file=get_test_image_file(),
        )

        response = self.client.get('/api/images/')
        self.assertEqual(response.status_code, 200)
        response_list = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_list, list)
        returned_title = response_list[0]['title']
        self.assertEqual(expected_title, returned_title)
        returned_file_url = response_list[0]['file']
        expected_file_name = image.file.name
        self.assertIn(expected_file_name, returned_file_url)

    def test_api_v1_single_image(self):
        response = self.client.get('/api/v1/images/')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'], 0)
        self.assertEqual(response_dict['images'], [])

        expected_title = "Test image"
        image = Image.objects.create(
            title=expected_title,
            file=get_test_image_file(),
        )

        response = self.client.get('/api/v1/images/')
        self.assertEqual(response.status_code, 200)
        response_dict = eval(response.content.decode(response.charset))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict['meta']['total_count'], 1)
        returned_title = response_dict['images'][0]['title']
        self.assertEqual(expected_title, returned_title)

