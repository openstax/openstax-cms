import os
import shutil

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import LiveServerTestCase, override_settings
from django.utils.six import StringIO
from selenium import webdriver
from social.apps.django_app.default.models import UserSocialAuth
from wagtail.tests.utils import WagtailPageTests

from .utils import create_user

TEST_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.create_user',
    'accounts.pipelines.save_profile',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)

class Utilities(LiveServerTestCase, WagtailPageTests):
    serialized_rollback = True

    def setUp(self):
        super(WagtailPageTests, self).setUp()
        super(LiveServerTestCase, self).setUp()

    def test_import_user(self):
        user_details = {'last_name': 'Hart',
                        'username': 'openstax_cms_tester',
                        'full_name': None,
                        'first_name': 'Richard',
                        'uid': 16180}
        # check user doesnt exist
        if User.objects.filter(username=user_details['username']).exists():
            User.objects.filter(username=user_details['username'])[0].delete()
        cursor = connection.cursor()
        cursor.execute("SELECT username FROM auth_user")
        db_users = cursor.fetchall()
        usernames = [username for (username,) in db_users]

        self.assertNotIn(user_details['username'], usernames)

        # create user
        returned_user = create_user(**user_details)

        # check the returned result
        self.assertTrue(
            User.objects.filter(username=user_details['username']).exists())
        # User.objects.get(username=user_details['username'])

        self.assertTrue(returned_user.social_auth.exists())
        social_user = returned_user.social_auth.first()
        self.assertEqual(social_user.uid, str(user_details['uid']))
        self.assertEqual(social_user.user.username, user_details['username'])

        # make sure changes are reflected in database
        cursor = connection.cursor()
        cursor.execute("SELECT username, last_name, first_name FROM auth_user")
        django_users = cursor.fetchall()
        returned_users = [set(user) for user in django_users]
        expected_user = set([user_details['username'],
                             user_details['last_name'],
                             user_details['first_name'], ])
        self.assertIn(expected_user, returned_users)
        cursor.execute(
            "SELECT provider, uid, user_id FROM social_auth_usersocialauth")
        ostax_acc_users = cursor.fetchall()
        returned_users = [set(user) for user in ostax_acc_users]
        expected_user = set(
            ['openstax', str(user_details['uid']), returned_user.pk])
        self.assertIn(expected_user, returned_users)

    def test_import_command(self):
        out = StringIO()
        # check yaml format
        self.assertFalse(User.objects.filter(username='username').exists())
        call_command('import_users', 'accounts/test_users.yaml', stdout=out)
        self.assertTrue(User.objects.filter(username='username').exists())
        new_user = User.objects.get(username='username')
        provider = new_user.social_auth.first()
        accounts_id = provider.uid
        returned_user = {'last_name': new_user.last_name,
                         'username': new_user.username,
                         'first_name': new_user.first_name,
                         'uid': accounts_id}
        expected_user = {'username': 'username',
                         'last_name': 'last_name',
                         'first_name': 'first_name',
                         'uid': '0'}
        self.assertEqual(expected_user, returned_user)

        # check csv format
        self.assertFalse(User.objects.filter(username='username_1').exists())
        call_command('import_users', 'accounts/test_users.csv', stdout=out)
        self.assertTrue(User.objects.filter(username='username_1').exists())
        new_user = User.objects.get(username='username_1')
        provider = new_user.social_auth.first()
        accounts_id = provider.uid
        returned_user = {'last_name': new_user.last_name,
                         'username': new_user.username,
                         'first_name': new_user.first_name,
                         'uid': accounts_id}
        expected_user = {'username': 'username_1',
                         'last_name': 'last_name_1',
                         'first_name': 'first_name_1',
                         'uid': '1'}
        self.assertEqual(expected_user, returned_user)

        new_user = User.objects.get(username='username_2')
        provider = new_user.social_auth.first()
        accounts_id = provider.uid
        returned_user = {'last_name': new_user.last_name,
                         'username': new_user.username,
                         'first_name': new_user.first_name,
                         'uid': accounts_id}
        expected_user = {'username': 'username_2',
                         'last_name': 'last_name_2',
                         'first_name': 'first_name_2',
                         'uid': '2'}
        self.assertEqual(expected_user, returned_user)


    def tearDown(self):
        super(WagtailPageTests, self).tearDown()
        super(LiveServerTestCase, self).tearDown()


@override_settings(SOCIAL_AUTH_LOGIN_REDIRECT_URL='/admin/',
                   SOCIAL_AUTH_PIPELINE=TEST_PIPELINE,
                   SESSION_COOKIE_DOMAIN=None,
                   SOCIAL_AUTH_LOGIN_URL='/')
class Integration(LiveServerTestCase, WagtailPageTests):
    serialized_rollback = True

    def setUp(self):
        super(WagtailPageTests, self).setUp()
        super(LiveServerTestCase, self).setUp()
        try:
            phantomjs_path = os.environ['phantomjs']
        except KeyError:
            phantomjs_path = shutil.which("phantomjs")
        self.driver = webdriver.PhantomJS(executable_path=phantomjs_path)

    def target(self, username, password):
        if User.objects.filter(username=username).exists():
            User.objects.get(username=username).delete()
        self.assertFalse(User.objects.filter(username=username).exists())
        driver = self.driver
        driver.get("http://localhost:8001/admin")
        self.assertEqual(
            driver.current_url, 'http://localhost:8001/admin/login/?next=/admin/')
        connect_button = driver.find_element_by_xpath('/html/body/div[1]/a')
        connect_button.click()
        username_field = driver.find_element_by_name("auth_key")
        username_field.send_keys(username)
        password_field = driver.find_element_by_name("password")
        password_field.send_keys(password)
        sign_in_button = driver.find_element_by_class_name("standard")
        sign_in_button.click()
        self.assertEqual(
            driver.current_url, 'http://localhost:8001/finish-profile/?next=/admin')
        self.assertTrue(User.objects.filter(username=username).exists())
        return User.objects.get(username=username)

    def test_oauth_login_create_user(self):
        USERNAME = 'openstax_cms_tester'
        PASSWORD = 'openstax_cms_tester'
        user = self.target(USERNAME, PASSWORD)
        self.assertEqual(user.username, USERNAME)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.driver.get('http://localhost:8001/api/user/?format=json')
        self.assertNotIn("Faculty", self.driver.page_source)

    def tearDown(self):
        self.driver.close()
        super(WagtailPageTests, self).tearDown()
        super(LiveServerTestCase, self).tearDown()



