from django.test import TestCase
from django.test import LiveServerTestCase
from wagtail.tests.utils import WagtailPageTests
from simple_salesforce import Salesforce as SimpleSalesforce
from .salesforce import Salesforce
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.utils.six import StringIO
from salesforce.models import Adopter

from django.conf import settings

class SalesforceTest(LiveServerTestCase,WagtailPageTests):
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
            self.assertEqual(status, u'Confirmed')

    def test_faculty_unknown(self):
        with Salesforce() as sf:
            status = sf.faculty_status(1)
            self.assertIsNone(status)

    def test_faculty_pending(self):
        with Salesforce() as sf:
            status = sf.faculty_status(2)
            self.assertEqual(status, u'Pending')

    def test_faculty_rejected(self):
        with Salesforce() as sf:
            status = sf.faculty_status(3)
            self.assertEqual(status, u'Rejected')

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
    def test_context_manager_handle_init_errors(self):
        with self.assertRaises(RuntimeError):
            Salesforce()


    def test_adopters(self):
        with Salesforce() as sf:
            adopters = sf.adopters()
        self.assertIsInstance(adopters,list)
        self.assertGreater(len(adopters),1)
        self.assertIn('Id',adopters[0].keys())
        self.assertIn('Name',adopters[0].keys())
        self.assertIn('Description',adopters[0].keys())
        self.assertIn('Website',adopters[0].keys())

    def test_update_adopters_command(self):
        out = StringIO()
        call_command('update_adopters', stdout=out)
        self.assertIn("Success", out.getvalue())      
        adopters = Adopter.objects.all()
        self.assertTrue(Adopter.objects.filter(name='Rice University').exists())

    def tearDown(self):
        super(WagtailPageTests, self).tearDown()
        super(LiveServerTestCase, self).tearDown()

