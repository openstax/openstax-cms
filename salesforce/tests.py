import datetime
import vcr
import json

from django.core.management import call_command
from django.test import LiveServerTestCase, TestCase, Client
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from books.models import BookIndex, Book
from pages.models import HomePage
from salesforce.models import SalesforceSettings, MapBoxDataset, Partner, AdoptionOpportunityRecord, SalesforceForms
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
