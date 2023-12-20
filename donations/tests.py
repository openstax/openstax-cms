from django.test import TestCase

from donations.models import DonationPopup, ThankYouNote, Fundraiser
from donations.serializers import DonationPopupSerializer, FundraiserSerializer

from rest_framework import status
from rest_framework.test import APITestCase


class DonationPopupTest(APITestCase, TestCase):

    def setUp(self):
        dp = DonationPopup.objects.create(
            download_image="books3x.max-165x165.png",
            download_ready="Your download is ready",
            header_image="data-science3x.max-165x165.png",
            header_title="Support as much as you can",
            header_subtitle="Give back to support more resources for all",
            give_link_text="Give Today",
            give_link="https://openstax.org/give",
            thank_you_link_text="Send a thank you note",
            thank_you_link="https://openstax.org",
            giving_optional="Giving is optionial",
            go_to_pdf_link_text="Go to PDF",
            hide_donation_popup=False
        )
        dp.save()

    def test_donation_api_get(self):
        response = self.client.get('/apps/cms/api/donations/donation-popup/', format='json')
        popup = DonationPopup.objects.all()
        serializer = DonationPopupSerializer(popup, many=True)
        self.assertEqual(response.data[0]['header_title'], serializer.data[0]['header_title'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ThankYouNoteTest(APITestCase, TestCase):

    def test_thank_you_note_api_post(self):
        data = {"thank_you_note":"OpenStax is the best! Loved not paying for a book", "last_name": "Drew", "first_name": "Jessica", "institution": "Rice University", "consent_to_share_or_contact": "True", "contact_email_address": "jess@example.com", "source": "PDF download"}
        response = self.client.post('/apps/cms/api/donations/thankyounote/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tyn = ThankYouNote.objects.filter(last_name='Drew').values()
        self.assertEqual(tyn[0]['first_name'], 'Jessica')
        self.assertEqual(tyn[0]['consent_to_share_or_contact'], True)
        self.assertEqual(tyn[0]['contact_email_address'], 'jess@example.com')


class FundraiserTest(APITestCase, TestCase):

    def setUp(self):
        fr = Fundraiser.objects.create(
            color_scheme="blue",
            message_type="goal",
            headline="this is a headline",
            message="Test message",
            button_text="Give Today",
            button_url="https://openstax.org/give",
            box_headline="This is a box headline",
            box_html="this goes <strong>in</strong> a box",
            fundraiser_image="data-science3x.max-165x165.png",
            goal_amount=2314,
            goal_time="2022-01-12T09:07:01-06:00"
        )
        fr.save()

    def test_fundraiser_api_get(self):
        response = self.client.get('/apps/cms/api/donations/fundraiser/', format='json')
        fundraiser = Fundraiser.objects.all()
        serializer = FundraiserSerializer(fundraiser, many=True)
        self.assertEqual(response.data[0]['headline'], serializer.data[0]['headline'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
