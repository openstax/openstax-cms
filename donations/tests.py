from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from donations.models import DonationPopup, ThankYouNote, Fundraiser, SiteBanner
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
        data = {"thank_you_note":"OpenStax is the best! Loved not paying for a book", "last_name": "Drew", "first_name": "Jessica", "school": "Rice University", "consent_to_share_or_contact": "True", "contact_email_address": "jess@example.com", "source": "PDF download"}
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


class SiteBannerTest(APITestCase, TestCase):

    def setUp(self):
        now = timezone.now()
        self.now = now

        self.active_in_window = SiteBanner.objects.create(
            name='active-in-window',
            html_message='active in window',
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
            is_active=True,
        )
        self.active_open_ended = SiteBanner.objects.create(
            name='active-open-ended',
            html_message='active no dates',
            is_active=True,
        )
        self.inactive = SiteBanner.objects.create(
            name='inactive',
            html_message='inactive',
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
            is_active=False,
        )
        self.not_yet_started = SiteBanner.objects.create(
            name='future',
            html_message='future',
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=7),
            is_active=True,
        )
        self.expired = SiteBanner.objects.create(
            name='expired',
            html_message='expired',
            start_date=now - timedelta(days=7),
            end_date=now - timedelta(days=1),
            is_active=True,
        )

    def test_returns_only_active_in_window_banners(self):
        response = self.client.get('/apps/cms/api/donations/sitebanner/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_names = {banner['name'] for banner in response.data}
        self.assertEqual(
            returned_names,
            {'active-in-window', 'active-open-ended'},
        )

    def test_inactive_banner_excluded(self):
        response = self.client.get('/apps/cms/api/donations/sitebanner/', format='json')
        returned_names = {banner['name'] for banner in response.data}
        self.assertNotIn('inactive', returned_names)

    def test_future_banner_excluded(self):
        response = self.client.get('/apps/cms/api/donations/sitebanner/', format='json')
        returned_names = {banner['name'] for banner in response.data}
        self.assertNotIn('future', returned_names)

    def test_expired_banner_excluded(self):
        response = self.client.get('/apps/cms/api/donations/sitebanner/', format='json')
        returned_names = {banner['name'] for banner in response.data}
        self.assertNotIn('expired', returned_names)

    def test_response_shape(self):
        response = self.client.get('/apps/cms/api/donations/sitebanner/', format='json')
        banner = next(b for b in response.data if b['name'] == 'active-in-window')
        expected_fields = {
            'id', 'name', 'html_message', 'link_text', 'link_url',
            'banner_thumbnail', 'is_active', 'start_date', 'end_date',
            'context_filter', 'url_pattern',
        }
        self.assertEqual(set(banner.keys()), expected_fields)
