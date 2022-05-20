import vcr
import unittest

from django.conf import settings
from django.core.management import call_command
from django.test import LiveServerTestCase, TestCase, Client
from six import StringIO
from django.core.exceptions import ValidationError

from salesforce.models import Adopter, SalesforceSettings, MapBoxDataset, Partner, AdoptionOpportunityRecord, PartnerReview, SalesforceForms
from salesforce.views import Salesforce
from salesforce.salesforce import Salesforce as SF
from salesforce.serializers import PartnerSerializer, AdoptionOpportunityRecordSerializer

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from wagtail.tests.utils import WagtailPageTests

from shared.test_utilities import mock_user_login


class PartnerTest(APITestCase, TestCase):

    def setUp(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/partners.yaml'):
            call_command('update_partners')
        for partner in Partner.objects.all():
            partner.visible_on_website = True
            partner.save()

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

    def test_can_add_review(self):
        review = PartnerReview.objects.create(partner=Partner.objects.first(),
                                              rating=5,
                                              review="This is a great resource.",
                                              submitted_by_name="Test McTester",
                                              submitted_by_account_uuid='aaa560a1-e828-48fb-b9a8-d01e9aec71d0')
        self.assertEqual(review.review, "This is a great resource.")

    def test_partners_include_review_data(self):
        random_partner = Partner.objects.order_by("?").first()
        response = self.client.get('/apps/cms/api/salesforce/partners/{}/'.format(random_partner.pk), format='json')
        self.assertIn('reviews', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('rating_count', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_partners_no_reviews(self):
        response = self.client.get('/apps/cms/api/salesforce/partners/', format='json')
        self.assertNotIn('reviews', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_only_submit_one_review_per_user(self):
        random_partner = Partner.objects.order_by("?").first()
        data = {"partner": random_partner.id, "rating": 4, "submitted_by_name": "Some User", "submitted_by_account_uuid": 'aaa560a1-e828-48fb-b9a8-d01e9aec71d0'}
        response = self.client.post('/apps/cms/api/salesforce/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {"partner": random_partner.id, "rating": 4, "submitted_by_name": "Some User",
                "submitted_by_account_uuid": 'aaa560a1-e828-48fb-b9a8-d01e9aec71d0'}
        response = self.client.post('/apps/cms/api/salesforce/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_delete_review(self):
        review = PartnerReview.objects.create(
            partner=Partner.objects.order_by("?").first(),
            rating=5,
            submitted_by_name="O. Staxly",
            submitted_by_account_uuid='aaa560a1-e828-48fb-b9a8-d01e9aec71d0' # accounts dev admin user uuid - special case to bypass SSO cookie check
        )
        response = self.client.delete('/apps/cms/api/salesforce/reviews/?id=' + str(review.id), format='json')
        self.assertEqual(response.data['status'], 'Deleted')


class SalesforceTest(LiveServerTestCase, WagtailPageTests):

    def setUp(self):
        mock_user_login()

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
        with vcr.use_cassette('fixtures/vcr_cassettes/contact.yaml'):
            sf = SF()
            contact_info = sf.query(
                "SELECT Id FROM Contact")
            self.assertIsNot(
                contact_info, None)

    def test_salesforce_forms_no_debug(self):
        form = SalesforceForms(oid='thisisanoid', posting_url='https://nowhereto.salesforce.com/nothing')
        form.save()
        response = self.client.get('/apps/cms/api/salesforce/forms/?format=json')
        self.assertIn(b"thisisanoid", response.content)

    def test_salesforce_forms_debug_validation_error(self):
        form = SalesforceForms(oid='thisisanoid', posting_url='https://nowhereto.salesforce.com/nothing', debug=True)
        try:
            form.save()
        except ValidationError as e:
            self.assertTrue('debug_email' in e.message_dict)


class MapboxTest(TestCase):
    def create_mapbox_setting(self, name="test", tileset_id="test", style_url="test"):
        return MapBoxDataset.objects.create(name=name, tileset_id=tileset_id, style_url=style_url)
    
    def test_mapbox_setting_creation(self):
        setting = self.create_mapbox_setting()
        self.assertTrue(isinstance(setting, MapBoxDataset))
        self.assertEqual(setting.__str__(), setting.name)


class AdoptionOpportunityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.opportunity = AdoptionOpportunityRecord(opportunity_id='0066f000015SSy5AAG',
                                                     book_name='US History',
                                                     account_uuid='f826f1b1-ead5-4594-82b3-df9a2753cb43',
                                                     fall_student_number=123,
                                                     spring_student_number=75,
                                                     summer_student_number=None)
        self.opportunity.save()

    def test_query_opportunity_by_account_uuid(self):
        response = self.client.get('/apps/cms/api/salesforce/renewal?account_uuid=f826f1b1-ead5-4594-82b3-df9a2753cb43')
        self.assertIn(b'"students": "123"', response.content)

