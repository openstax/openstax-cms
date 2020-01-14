import unittest

from django.conf import settings
from django.core.management import call_command
from django.test import LiveServerTestCase, TestCase
from django.utils.six import StringIO
from django.core.exceptions import ValidationError

from salesforce.models import Adopter, SalesforceSettings, MapBoxDataset, Partner
from salesforce.views import Salesforce
from simple_salesforce import Salesforce as SimpleSalesforce
from salesforce.serializers import PartnerSerializer

from rest_framework import status
from rest_framework.test import APITestCase
from wagtail.tests.utils import WagtailPageTests

class AdopterTest(TestCase):

    def create_adopter(self, sales_id="123", name="test", description="test", website="https://rice.edu"):
        return Adopter.objects.create(sales_id=sales_id, name=name, description=description, website=website)

    def test_adopter_creation(self):
        adopter = self.create_adopter()
        self.assertTrue(isinstance(adopter, Adopter))
        self.assertEqual(adopter.__str__(), adopter.name)


class PartnerTest(APITestCase, TestCase):

    def setUp(self):
        call_command('update_partners')

    def test_did_update_partners(self):
        self.assertGreater(Partner.objects.all().count(), 0)

    def test_partners_api_get_all_partners(self):
        response = self.client.get('/apps/cms/api/salesforce/partners/', format='json')
        partners = Partner.objects.all()
        serializer = PartnerSerializer(partners, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partners_api_get_one_partner(self):
        random_partner = Partner.objects.order_by("?").first()
        response = self.client.get('/apps/cms/api/salesforce/partners/{}/'.format(random_partner.pk), format='json')
        serializer = PartnerSerializer(random_partner)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partners_invalid_partner(self):
        invalid_partner_id = Partner.objects.order_by("id").last().id + 1
        response = self.client.get('/apps/cms/api/salesforce/partners/{}/'.format(invalid_partner_id), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


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

    def tearDown(self):
        super(WagtailPageTests, self).tearDown()
        super(LiveServerTestCase, self).tearDown()


class MapboxTest(TestCase):
    def create_mapbox_setting(self, name="test", tileset_id="test", style_url="test"):
        return MapBoxDataset.objects.create(name=name, tileset_id=tileset_id, style_url=style_url)
    
    def test_mapbox_setting_creation(self):
        setting = self.create_mapbox_setting()
        self.assertTrue(isinstance(setting, MapBoxDataset))
        self.assertEqual(setting.__str__(), setting.name)