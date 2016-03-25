from django.test import LiveServerTestCase
from wagtail.tests.utils import WagtailPageTests
from simple_salesforce import Salesforce as SimpleSalesforce
from .salesforce import Salesforce
from django.test import override_settings
from django.core.management import call_command
from django.utils.six import StringIO
from salesforce.models import Adopter
import unittest
from django.conf import settings
from django.contrib.auth.models import User, Group
from accounts.utils import create_user
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


class SalesforceTest(LiveServerTestCase, WagtailPageTests):

    def setUp(self):
        super(WagtailPageTests, self).setUp()
        super(LiveServerTestCase, self).setUp()

    def test_login(self):
        sf = SimpleSalesforce(**settings.SALESFORCE)
        self.assertEqual(sf.sf_instance, u'na12.salesforce.com')

    def test_database_query(self):
        sf = SimpleSalesforce(**settings.SALESFORCE)
        contact_info = sf.query(
            "SELECT Id FROM Contact WHERE Accounts_ID__c = '0'")
        self.assertEqual(
            contact_info['records'][0]['Id'], u'003U000001erXyqIAE')

    def test_faculty_confirmed(self):
        with Salesforce() as sf:
            status = sf.faculty_status(0)
            self.assertEqual(status, ['0'])

    def test_faculty_unknown(self):
        with Salesforce() as sf:
            status = sf.faculty_status(1)
            self.assertEqual(status, [])

    def test_faculty_pending(self):
        with Salesforce() as sf:
            status = sf.faculty_status(2)
            self.assertEqual(status, [])

    def test_faculty_rejected(self):
        with Salesforce() as sf:
            status = sf.faculty_status(3)
            self.assertEqual(status, [])

    @unittest.skip("logs need to be configured")
    def test_context_manager(self):
        with open(settings.LOGGING['handlers']['file']['filename'], 'r') as f:
            lines = f.readlines()
            if lines:
                last_message = lines[-1]
            else:
                last_message = None
        with self.assertRaises(RuntimeError):
            with Salesforce() as sf:
                raise RuntimeError("test context manager error handling")
        with open(settings.LOGGING['handlers']['file']['filename'], 'r') as f:
            lines = f.readlines()
            new_message = lines[-1]
        self.assertNotEqual(last_message, new_message)
        self.assertIn("test context manager error handling", new_message)

    @override_settings(SALESFORCE={})
    @unittest.skip("logs need to be configured")
    def test_context_manager_handle_init_errors(self):
        with self.assertRaises(RuntimeError):
            Salesforce()

    def test_adopters(self):
        with Salesforce() as sf:
            adopters = sf.adopters()
        self.assertIsInstance(adopters, list)
        self.assertGreater(len(adopters), 1)
        self.assertIn('Id', adopters[0].keys())
        self.assertIn('Name', adopters[0].keys())
        self.assertIn('Description', adopters[0].keys())
        self.assertIn('Website', adopters[0].keys())

    def test_update_adopters_command(self):
        out = StringIO()
        call_command('update_adopters', stdout=out)
        self.assertIn("Success", out.getvalue())
        Adopter.objects.all()
        self.assertTrue(
            Adopter.objects.filter(name='Rice University').exists())

    def test_update_faculty_status_command(self):
        test_user = {'last_name': 'last_name',
                     'username': 'username',
                     'full_name': None,
                     'first_name': 'first_name',
                     'uid': 0}
        result = create_user(**test_user)
        returned_user = result['user']
        out = StringIO()
        cms_id = str(returned_user.pk)
        self.assertFalse(returned_user.groups.filter(name='Faculty').exists())
        call_command(
            'update_faculty_status', cms_id, stdout=out)
        self.assertIn("Success", out.getvalue())
        self.assertTrue(returned_user.groups.filter(name='Faculty').exists())

    def test_update_faculty_status_all_command(self):
        from accounts.utils import create_user
        user_details = {'last_name': 'Hart',
                        'username': 'openstax_cms_faculty_tester',
                        'full_name': None,
                        'first_name': 'Richard',
                        'uid': 16207}
        result = create_user(**user_details)
        test_user = result['user']
        self.assertFalse(test_user.groups.filter(name='Faculty').exists())
        out = StringIO()
        call_command('update_faculty_status', '--all', stdout=out)
        self.assertIn("Success", out.getvalue())
        test_user = User.objects.filter(username=user_details['username'])[0]
        self.assertTrue(test_user.groups.filter(name='Faculty').exists())

    def test_context_manager_session(self):
        from django.contrib.sessions.backends.db import SessionStore
        with Salesforce() as sf:
            returned_session_id = sf.session_id
        sesson_store = SessionStore(Salesforce._default_session_key)
        self.assertIn('sf_instance', sesson_store.keys())
        for i in range(0, 5):
            with Salesforce() as sf:
                expected_session_id = returned_session_id
                returned_session_id = sf.session_id
                self.assertEqual(expected_session_id, returned_session_id)

        original_session = Salesforce._default_session_key
        with self.assertRaises(RuntimeError):
            with Salesforce() as sf:
                raise RuntimeError
        self.assertNotEqual(original_session, Salesforce._default_session_key)

    def tearDown(self):
        super(WagtailPageTests, self).tearDown()
        super(LiveServerTestCase, self).tearDown()

