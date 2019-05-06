import unittest

from django.conf import settings
from django.core.management import call_command
from django.test import LiveServerTestCase, TestCase
from django.utils.six import StringIO
from django.core.exceptions import ValidationError
from salesforce.models import Adopter, SalesforceSettings
from salesforce.views import Salesforce
from simple_salesforce import Salesforce as SimpleSalesforce
from wagtail.tests.utils import WagtailPageTests

class AdopterTest(TestCase):

    def create_adopter(self, sales_id="123", name="test", description="test", website="https://rice.edu"):
        return Adopter.objects.create(sales_id=sales_id, name=name, description=description, website=website)

    def test_adopter_creation(self):
        adopter = self.create_adopter()
        self.assertTrue(isinstance(adopter, Adopter))
        self.assertEqual(adopter.__str__(), adopter.name)


class SalesforceTest(LiveServerTestCase, WagtailPageTests):

    def setUp(self):
        super(WagtailPageTests, self).setUp()
        super(LiveServerTestCase, self).setUp()

    def create_salesforce_setting(self, username="test", password="test", security_token="test",
                                                     sandbox=True):
        return SalesforceSettings.objects.create(username=username, password=password, security_token=security_token,
                                                     sandbox=sandbox)

    def test_salesforce_setting_creation(self):
        setting = self.create_salesforce_setting()
        self.assertTrue(isinstance(setting, SalesforceSettings))
        self.assertEqual(setting.__str__(), setting.username)

    def test_can_only_create_one_instance(self):
        setting1 = self.create_salesforce_setting()
        with self.assertRaises(ValidationError):
            self.create_salesforce_setting(username="test2", password="test2", security_token="test2", sandbox=False)

    def test_login(self):
        sf = SimpleSalesforce(**settings.SALESFORCE)
        self.assertEqual(sf.sf_instance, u'cs4.salesforce.com')

    def test_database_query(self):
        sf = SimpleSalesforce(**settings.SALESFORCE)
        contact_info = sf.query(
            "SELECT Id FROM Contact")
        self.assertIsNot(
            contact_info, None)

    def test_update_adopters_command(self):
        out = StringIO()
        call_command('update_adopters', stdout=out)
        self.assertIn("Success", out.getvalue())
        Adopter.objects.all()
        self.assertTrue(
            Adopter.objects.filter(name='Rice University').exists())

    def tearDown(self):
        super(WagtailPageTests, self).tearDown()
        super(LiveServerTestCase, self).tearDown()

