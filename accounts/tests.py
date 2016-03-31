from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import LiveServerTestCase
from django.utils.six import StringIO
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

        usernames = User.objects.all()
        self.assertNotIn(user_details['username'], usernames)

        # create user
        returned_user = create_user(**user_details)

        # check the returned result
        self.assertTrue(
            User.objects.filter(username=user_details['username']).exists())

        self.assertTrue(returned_user.social_auth.exists())
        social_user = returned_user.social_auth.first()
        self.assertEqual(social_user.uid, str(user_details['uid']))
        self.assertEqual(social_user.user.username, user_details['username'])

        # make sure changes are reflected in database
        returned_users = User.objects.values('username', 'last_name', 'first_name')
        expected_user = {'last_name': user_details['last_name'],
                         'first_name': user_details['first_name'],
                         'username': user_details['username']
                         }
        self.assertIn(expected_user, returned_users)

        returned_users = UserSocialAuth.objects.values('provider', 'uid', 'user_id')

        expected_user = {'user_id': returned_user.pk,
                         'provider': 'openstax',
                         'uid': str(user_details['uid'])
                         }
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
