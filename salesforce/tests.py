import datetime
import vcr
import json
from unittest.mock import patch

from django.core.management import call_command
from django.test import LiveServerTestCase, TestCase, Client
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from books.models import BookIndex, Book
from pages.models import HomePage
from salesforce.models import SalesforceSettings, MapBoxDataset, Partner, AdoptionOpportunityRecord, SalesforceForms, School
from salesforce.salesforce import Salesforce as SF
from salesforce.serializers import PartnerSerializer

from rest_framework import status
from rest_framework.test import APITestCase

from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page
from wagtail.documents.models import Document


from shared.test_utilities import mock_user_login


def redact_sensitive_info(request):
    # Check if the request has a body
    if request.body:
        # Decode the body to a string for manipulation
        body = request.body.decode('utf-8')

        # Replace the specific sensitive value
        body = body.replace(settings.SALESFORCE['password'], "")
        body = body.replace(settings.SALESFORCE['security_token'], "")
        body = body.replace(settings.SALESFORCE['username'], "")

        # Encode the body back to bytes
        request.body = body.encode('utf-8')

    return request


openstax_vcr = vcr.VCR(
    record_mode='once',
    filter_headers=['Authorization', 'uri', 'body'],
    before_record_request=redact_sensitive_info

)


class PartnerTest(APITestCase, TestCase):

    def setUp(self):
        with openstax_vcr.use_cassette('fixtures/vcr_cassettes/partners.yaml'):
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


class SalesforceTest(LiveServerTestCase, WagtailPageTestCase):

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
        with openstax_vcr.use_cassette('fixtures/vcr_cassettes/contact.yaml'):
            sf = SF()
            contact_info = sf.query("SELECT Id FROM Contact LIMIT 1")
            self.assertIsNot(contact_info, None)

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


class UpdateSchoolsCommandTest(TestCase):
    def sf_school(self, **overrides):
        school = {
            'Id': '001duplicate',
            'Name': 'Salesforce School',
            'Phone': '555-1212',
            'Website': 'https://example.edu',
            'Type': 'College',
            'Industry': 'HE',
            'School_Location__c': 'Urban',
            'Students_Current_Year__c': '123',
            'Total_School_Enrollment__c': '4567',
            'BillingCountry': 'United States',
            'BillingStreet': '123 Main St',
            'BillingCity': 'Houston',
            'BillingState': 'TX',
            'BillingPostalCode': '77030',
            'BillingLatitude': '29.720',
            'BillingLongitude': '-95.397',
            'Research_Agreement_Start_Date__c': datetime.date(2026, 1, 1),
            'Research_Agreement_End_Date__c': datetime.date(2026, 12, 31),
        }
        school.update(overrides)
        return school

    @patch('salesforce.management.commands.update_schools.invalidate_cloudfront_caches')
    @patch('salesforce.management.commands.update_schools.Salesforce')
    def test_update_schools_updates_first_duplicate_salesforce_id(self, salesforce, _invalidate):
        first_school = School.objects.create(salesforce_id='001duplicate', name='First duplicate')
        second_school = School.objects.create(salesforce_id='001duplicate', name='Second duplicate')

        sf = salesforce.return_value.__enter__.return_value
        sf.bulk.Account.query.return_value = [[self.sf_school()]]

        call_command('update_schools')

        first_school.refresh_from_db()
        second_school.refresh_from_db()
        self.assertEqual(first_school.name, 'Salesforce School')
        self.assertEqual(second_school.name, 'Second duplicate')
        self.assertEqual(School.objects.filter(salesforce_id='001duplicate').count(), 2)


class AdoptionOpportunityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.opportunity = AdoptionOpportunityRecord(opportunity_id='0066f000015SSy5AAG',
                                                     book_name='US History',
                                                     account_uuid='f826f1b1-ead5-4594-82b3-df9a2753cb43',
                                                     students=123)
        self.opportunity.save()

    def test_query_opportunity_by_account_uuid(self):
        response = self.client.get('/apps/cms/api/salesforce/renewal/?account_uuid=f826f1b1-ead5-4594-82b3-df9a2753cb43')
        self.assertIn(b'"students": "123"', response.content)


class UpdateOpportunitiesCommandTest(TestCase):
    ACCOUNT_A = 'f826f1b1-ead5-4594-82b3-df9a2753cb43'
    ACCOUNT_B = '310bb96b-0df8-4d10-a759-c7d366c1f524'

    def sf_adoption(self, **overrides):
        record = {
            'Id': 'a00Pc00000mPq01AL',
            'Adoption_Type__c': 'Confirmed',
            'Base_Year__c': 2024,
            'Confirmation_Date__c': None,
            'Confirmation_Type__c': 'OpenStax Confirmed Adoption',
            'How_Using__c': 'As the primary textbook',
            'Savings__c': None,
            'Students__c': 50,
            'Opportunity__r': {
                'StageName': 'Confirmed Adoption Won',
                'Book__r': {'Name': 'US History', 'Active__c': True},
                'Contact__r': {'Accounts_UUID__c': self.ACCOUNT_A},
            },
        }
        record.update(overrides)
        return record

    def run_command(self, past_results, current_results):
        with patch('salesforce.management.commands.update_opportunities.invalidate_cloudfront_caches'), \
                patch('salesforce.management.commands.update_opportunities.Salesforce') as salesforce:
            sf = salesforce.return_value.__enter__.return_value
            sf.bulk.Adoption__c.query.side_effect = [past_results, current_results]
            call_command('update_opportunities')

    def test_existing_opportunity_is_updated_not_duplicated(self):
        # A row already exists for this Salesforce Adoption Id, but with a stale
        # book name. Previously the multi-field lookup missed and the insert
        # collided on the unique opportunity_id, raising IntegrityError.
        AdoptionOpportunityRecord.objects.create(
            opportunity_id='a00Pc00000mPq01AL',
            book_name='Old Book Name',
            account_uuid=self.ACCOUNT_A,
            students=10,
        )

        self.run_command([self.sf_adoption(Students__c=99)], [])

        records = AdoptionOpportunityRecord.objects.filter(opportunity_id='a00Pc00000mPq01AL')
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first().book_name, 'US History')
        self.assertEqual(records.first().students, 99)

    def test_opportunity_id_stored_as_plain_string(self):
        self.run_command([self.sf_adoption()], [])
        self.assertTrue(
            AdoptionOpportunityRecord.objects.filter(opportunity_id='a00Pc00000mPq01AL').exists()
        )

    def test_inactive_book_is_skipped(self):
        record = self.sf_adoption()
        record['Opportunity__r']['Book__r']['Active__c'] = False
        self.run_command([record], [])
        self.assertEqual(AdoptionOpportunityRecord.objects.count(), 0)

    def test_current_adopter_replaces_stale_rows(self):
        # Past pass seeds last year's nudge data for account A.
        past = self.sf_adoption(Id='a00past', Base_Year__c=2024)
        # Current pass: account A confirmed this year with a different adoption.
        current = self.sf_adoption(Id='a00current', Base_Year__c=2025, Students__c=75)

        self.run_command([past], [current])

        records = AdoptionOpportunityRecord.objects.filter(account_uuid=self.ACCOUNT_A)
        # The stale last-year row was cleared and replaced by the current one.
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first().opportunity_id, 'a00current')
        self.assertEqual(records.first().students, 75)

    def test_badly_formatted_uuid_is_skipped(self):
        record = self.sf_adoption()
        record['Opportunity__r']['Contact__r']['Accounts_UUID__c'] = 'not-a-uuid'
        self.run_command([record], [])
        self.assertEqual(AdoptionOpportunityRecord.objects.count(), 0)


class ResourceDownloadTest(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        # create root page
        root_page = Page.objects.get(title="Root")
        # create homepage
        homepage = HomePage(title="Hello World",
                            slug="hello-world",
                            )
        # add homepage to root page
        root_page.add_child(instance=homepage)
        # create book index page
        book_index = BookIndex(title="Book Index",
                               page_description="Test",
                               dev_standard_1_description="Test",
                               dev_standard_2_description="Test",
                               dev_standard_3_description="Test",
                               dev_standard_4_description="Test",
                               )
        # add book index to homepage
        homepage.add_child(instance=book_index)
        test_image = SimpleUploadedFile(name='openstax.png',
                                        content=open("pages/static/images/openstax.png", 'rb').read())
        cls.test_doc = Document.objects.create(title='Test Doc', file=test_image)

    def test_resource_download_post(self):
        root_page = Page.objects.get(title="Root")
        book_index = BookIndex.objects.all()[0]
        book = Book(title="University Physics",
                    slug="university-physics",
                    cnx_id='031da8d3-b525-429c-80cf-6c8ed997733a',
                    salesforce_book_id='',
                    description="Test Book",
                    cover=self.test_doc,
                    title_image=self.test_doc,
                    publish_date=datetime.date.today(),
                    locale=root_page.locale
                    )
        book_index.add_child(instance=book)
        data = {
            "book": book.pk,
            "book_format": "PDF",
            "account_uuid": "310bb96b-0df8-4d10-a759-c7d366c1f524",
            "resource_name": "Book PDF",
            "contact_id": "0032f00003zYVdSAAZ"
            }
        response = self.client.post('/apps/cms/api/salesforce/download-tracking/', data, format='json')
        self.assertEqual("PDF", response.data['book_format'])
