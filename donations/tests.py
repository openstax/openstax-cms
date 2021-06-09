from django.test import TestCase

from donations.models import DonationPopup, ThankYouNote
from donations.serializers import DonationPopupSerializer

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
        data = {"thank_you_note":"OpenStax is the best! Loved not paying for a book", "last_name": "Drew", "first_name": "Jessica", "institution": "Rice University"}
        response = self.client.post('/apps/cms/api/donations/thankyounote/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tyn = ThankYouNote.objects.filter(last_name='Drew').values()
        self.assertEqual(tyn[0]['first_name'], 'Jessica')
