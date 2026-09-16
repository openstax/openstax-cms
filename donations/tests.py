from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from donations.models import DonationPopup, DonationLink, ThankYouNote, Fundraiser, SiteBanner
from donations.serializers import DonationPopupSerializer, DonationLinkSerializer, FundraiserSerializer

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


class DonationPopupSingletonTest(APITestCase, TestCase):
    """A second DonationPopup must surface as a normal form error in the
    Wagtail admin (CORE-1390), not the 500 that raising only from save()
    produced: form validation runs, saves, and only then does .save() get a
    chance to object."""

    def setUp(self):
        self.existing = DonationPopup.objects.create(
            download_ready="Your download is ready",
            header_title="Support as much as you can",
            header_subtitle="Give back to support more resources for all",
            give_link_text="Give Today",
            give_link="https://openstax.org/give",
            thank_you_link_text="Send a thank you note",
            thank_you_link="https://openstax.org",
            giving_optional="Giving is optional",
            go_to_pdf_link_text="Go to PDF",
            hide_donation_popup=False,
        )

    def test_full_clean_raises_when_a_popup_already_exists(self):
        second = DonationPopup(
            download_ready="Your download is ready",
            header_title="Support as much as you can",
            header_subtitle="Give back to support more resources for all",
            give_link_text="Give Today",
            give_link="https://openstax.org/give",
            thank_you_link_text="Send a thank you note",
            thank_you_link="https://openstax.org",
            giving_optional="Giving is optional",
            go_to_pdf_link_text="Go to PDF",
        )
        with self.assertRaisesMessage(ValidationError, 'There can be only one donation popup instance'):
            second.full_clean()

    def test_save_still_guards_programmatic_creation(self):
        # Backstop for callers that bypass a ModelForm (scripts, shell, data migrations).
        with self.assertRaisesMessage(ValidationError, 'There can be only one donation popup instance'):
            DonationPopup.objects.create(
                download_ready="Your download is ready",
                header_title="Support as much as you can",
                header_subtitle="Give back to support more resources for all",
                give_link_text="Give Today",
                give_link="https://openstax.org/give",
                thank_you_link_text="Send a thank you note",
                thank_you_link="https://openstax.org",
                giving_optional="Giving is optional",
                go_to_pdf_link_text="Go to PDF",
            )

    def test_admin_add_view_returns_form_error_not_500(self):
        self.client.force_login(
            User.objects.create_superuser("popupadmin", "popup@openstax.org", "pw")
        )
        data = {
            "download_ready": "Your download is ready",
            "header_title": "Support as much as you can",
            "header_subtitle": "Give back to support more resources for all",
            "give_link_text": "Give Today",
            "give_link": "https://openstax.org/give",
            "thank_you_link_text": "Send a thank you note",
            "thank_you_link": "https://openstax.org",
            "giving_optional": "Giving is optional",
            "go_to_pdf_link_text": "Go to PDF",
        }
        response = self.client.post(reverse("donationpopup:add"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "There can be only one donation popup instance")
        # No second row was created.
        self.assertEqual(DonationPopup.objects.count(), 1)


class DonationLinkTest(APITestCase, TestCase):
    """Uses its own variant names (distinct from the 8 seeded by migration
    0014) so assertions don't get tangled up with that seed data."""

    def setUp(self):
        self.active_control = DonationLink.objects.create(
            placement="pdf",
            variant="test-control",
            url="https://riceconnect.rice.edu/donation/support-openstax-subject",
            is_active=True,
        )
        self.active_public_good = DonationLink.objects.create(
            placement="pdf",
            variant="test-public-good",
            url="https://riceconnect.rice.edu/donation/support-openstax-subject-b",
            give_link_text="Give $50",
            header_title="Support as much as you can",
            header_subtitle="Join us in sustaining OpenStax as a public good for years to come by giving today.",
            header_image="data-science3x.max-165x165.png",
            is_active=True,
        )
        self.inactive = DonationLink.objects.create(
            placement="other",
            variant="test-inactive",
            url="https://riceconnect.rice.edu/donation/support-openstax-subject",
            is_active=False,
        )

    def test_str_uses_placement_display_and_variant(self):
        self.assertEqual(str(self.active_control), "PDF Download Popup - test-control")

    def test_placement_and_variant_must_be_unique_together(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            DonationLink.objects.create(
                placement="pdf",
                variant="test-control",
                url="https://riceconnect.rice.edu/donation/support-openstax-subject",
            )

    def test_serializer_output_shape(self):
        data = DonationLinkSerializer(self.active_control).data
        self.assertEqual(
            set(data.keys()),
            {
                "placement", "variant", "header_image", "url", "give_link_text",
                "header_title", "header_subtitle", "is_active",
            },
        )
        self.assertEqual(data["placement"], "pdf")
        self.assertEqual(data["variant"], "test-control")
        self.assertEqual(data["give_link_text"], "")
        self.assertFalse(data["header_image"])

    def test_serializer_round_trips_give_link_text(self):
        data = DonationLinkSerializer(self.active_public_good).data
        self.assertEqual(data["give_link_text"], "Give $50")

    def test_single_line_popup_fields_render_as_text_inputs(self):
        """They are TextFields for historical reasons, so without a widget override
        Wagtail gives a URL or a path a full textarea."""
        from django.forms import Textarea, TextInput

        from donations.wagtail_hooks import DonationPopupViewSet

        form_class = DonationPopupViewSet().get_form_class()
        widgets = form_class().fields

        for name in ('give_link', 'thank_you_link', 'header_title', 'download_ready'):
            self.assertIsInstance(
                widgets[name].widget, TextInput, f'{name} should be a single-line input'
            )

        # the subtitle really is prose, so it keeps its textarea
        self.assertIsInstance(widgets['header_subtitle'].widget, Textarea)

    def test_a_variant_may_leave_its_url_blank(self):
        """Blank means "use the Donation Popup's link", which is what lets a variant
        test copy or imagery without repeating the destination. The frontend already
        falls back on a blank value, so the field must not be required."""
        link = DonationLink(
            placement='pdf', variant='copy-only', url='',
            give_link_text='Give $50'
        )
        link.full_clean()
        link.save()

        row = next(
            item for item in self.client.get('/apps/cms/api/donations/donation-links/').json()
            if item['variant'] == 'copy-only'
        )

        self.assertEqual('', row['url'])
        self.assertEqual('Give $50', row['give_link_text'])

    def test_serializer_round_trips_header_image(self):
        data = DonationLinkSerializer(self.active_public_good).data
        self.assertIn("data-science3x.max-165x165.png", data["header_image"])

    def test_serializer_round_trips_header_title(self):
        data = DonationLinkSerializer(self.active_public_good).data
        self.assertEqual(data["header_title"], "Support as much as you can")

    def test_donation_links_api_returns_only_active_rows(self):
        response = self.client.get('/apps/cms/api/donations/donation-links/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        variants = {(row['placement'], row['variant']) for row in response.data}
        self.assertIn(('pdf', 'test-control'), variants)
        self.assertIn(('pdf', 'test-public-good'), variants)
        self.assertNotIn(('other', 'test-inactive'), variants)

    def test_donation_links_api_field_shape(self):
        response = self.client.get('/apps/cms/api/donations/donation-links/', format='json')
        row = next(r for r in response.data if r['variant'] == 'test-public-good')
        self.assertEqual(
            set(row.keys()),
            {
                "placement", "variant", "header_image", "url", "give_link_text",
                "header_title", "header_subtitle", "is_active",
            },
        )
        self.assertEqual(row['give_link_text'], "Give $50")
        self.assertEqual(row['header_title'], "Support as much as you can")
        self.assertEqual(
            row['header_subtitle'],
            "Join us in sustaining OpenStax as a public good for years to come by giving today.",
        )
        self.assertIn("data-science3x.max-165x165.png", row['header_image'])

    def test_donation_links_api_give_link_text_blank_on_unset_rows(self):
        response = self.client.get('/apps/cms/api/donations/donation-links/', format='json')
        row = next(r for r in response.data if r['variant'] == 'test-control')
        self.assertEqual(row['give_link_text'], "")

    def test_donation_links_api_header_image_falsy_on_unset_rows(self):
        response = self.client.get('/apps/cms/api/donations/donation-links/', format='json')
        row = next(r for r in response.data if r['variant'] == 'test-control')
        self.assertIn('header_image', row)
        self.assertFalse(row['header_image'])

    def test_donation_links_api_header_title_blank_on_unset_rows(self):
        response = self.client.get('/apps/cms/api/donations/donation-links/', format='json')
        row = next(r for r in response.data if r['variant'] == 'test-control')
        self.assertEqual(row['header_title'], "")


class DonationLinkSeedMigrationTest(TestCase):
    """Migration 0014 must reproduce the pre-existing hardcoded os-webview
    give-link pairs exactly, so behavior is unchanged on deploy."""

    def test_seeded_rows_match_previously_hardcoded_links(self):
        expected = {
            ('pdf', 'control'): ('https://riceconnect.rice.edu/donation/support-openstax-subject', ''),
            ('pdf', 'public good'): (
                'https://riceconnect.rice.edu/donation/support-openstax-subject-b',
                'Join us in sustaining OpenStax as a public good for years to come by giving today.',
            ),
            ('instructor_resources', 'control'): (
                'https://riceconnect.rice.edu/donation/support-openstax-instructor-resources', '',
            ),
            ('instructor_resources', 'public good'): (
                'https://riceconnect.rice.edu/donation/support-openstax-instructor-resources-b',
                'Join us in sustaining OpenStax as a public good for years to come by giving today.',
            ),
            ('student_resources', 'control'): (
                'https://riceconnect.rice.edu/donation/support-openstax-student-resources', '',
            ),
            ('student_resources', 'public good'): (
                'https://riceconnect.rice.edu/donation/support-openstax-student-resources-b',
                'Join us in sustaining OpenStax as a public good for years to come by giving today.',
            ),
            ('other', 'control'): ('https://riceconnect.rice.edu/donation/support-openstax-subject', ''),
            ('other', 'public good'): (
                'https://riceconnect.rice.edu/donation/support-openstax-subject-b',
                'Join us in sustaining OpenStax as a public good for years to come by giving today.',
            ),
        }
        self.assertEqual(DonationLink.objects.count(), len(expected))
        for (placement, variant), (url, header_subtitle) in expected.items():
            link = DonationLink.objects.get(placement=placement, variant=variant)
            self.assertEqual(link.url, url)
            self.assertEqual(link.header_subtitle, header_subtitle)
            self.assertEqual(link.give_link_text, '')
            self.assertEqual(link.header_title, '')
            self.assertTrue(link.is_active)

    def test_deleting_a_donation_link_invalidates_the_cached_list(self):
        from unittest.mock import patch

        link = DonationLink.objects.create(
            placement='pdf', variant='temporary', url='https://example.com/temp'
        )

        with patch('donations.signals.invalidate_cloudfront_caches') as invalidate:
            link.delete()

        invalidate.assert_called_with('donations/donation-links')

    def test_rollback_leaves_edited_rows_alone(self):
        from importlib import import_module

        from django.apps import apps

        migration = import_module('donations.migrations.0014_seed_donation_links')
        edited = DonationLink.objects.filter(placement='pdf', variant='control').first()
        edited.url = 'https://example.com/edited-by-an-editor'
        edited.save()

        migration.remove_seeded_donation_links(apps, None)

        self.assertTrue(
            DonationLink.objects.filter(pk=edited.pk).exists(),
            'a row an editor changed must survive a rollback'
        )
        self.assertFalse(
            DonationLink.objects.filter(placement='other', variant='control').exists(),
            'untouched seeded rows should still be removed'
        )

    def test_seeded_rows_give_link_text_blank_through_api(self):
        response = self.client.get('/apps/cms/api/donations/donation-links/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = next(r for r in response.data if r['placement'] == 'pdf' and r['variant'] == 'control')
        self.assertEqual(row['give_link_text'], '')

    def test_seeded_rows_header_image_falsy_through_api(self):
        response = self.client.get('/apps/cms/api/donations/donation-links/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = next(r for r in response.data if r['placement'] == 'pdf' and r['variant'] == 'control')
        self.assertIn('header_image', row)
        self.assertFalse(row['header_image'])

    def test_seeded_rows_header_title_blank_through_api(self):
        response = self.client.get('/apps/cms/api/donations/donation-links/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = next(r for r in response.data if r['placement'] == 'pdf' and r['variant'] == 'control')
        self.assertEqual(row['header_title'], '')


class ThankYouNoteTest(APITestCase, TestCase):

    def test_thank_you_note_api_post(self):
        data = {"thank_you_note":"OpenStax is the best! Loved not paying for a book", "last_name": "Drew", "first_name": "Jessica", "school": "Rice University", "consent_to_share_or_contact": "True", "contact_email_address": "jess@example.com", "source": "PDF download"}
        response = self.client.post('/apps/cms/api/donations/thankyounote/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tyn = ThankYouNote.objects.filter(last_name='Drew').values()
        self.assertEqual(tyn[0]['first_name'], 'Jessica')
        self.assertEqual(tyn[0]['consent_to_share_or_contact'], True)
        self.assertEqual(tyn[0]['contact_email_address'], 'jess@example.com')
        self.assertIsNone(tyn[0]['account_uuid'])

    def test_thank_you_note_api_post_stores_account_uuid_when_provided(self):
        account_uuid = "11111111-1111-1111-1111-111111111111"
        data = {"thank_you_note": "Thanks OpenStax!", "last_name": "Reed", "first_name": "Robin", "school": "Rice University", "source": "PDF download", "account_uuid": account_uuid}
        response = self.client.post('/apps/cms/api/donations/thankyounote/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tyn = ThankYouNote.objects.get(last_name='Reed')
        self.assertEqual(str(tyn.account_uuid), account_uuid)


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


class ThankYouNotePostHogTest(APITestCase, TestCase):
    @mock.patch('donations.signals.posthog_capture')
    def test_thank_you_note_post_fires_posthog_event(self, mock_capture):
        data = {
            "thank_you_note": "Thanks OpenStax!",
            "last_name": "Drew",
            "first_name": "Jessica",
            "school": "Rice University",
            "consent_to_share_or_contact": "True",
            "contact_email_address": "jess@example.com",
            "source": "PDF download",
        }
        response = self.client.post(
            '/apps/cms/api/donations/thankyounote/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_capture.assert_called_once()
        self.assertEqual(mock_capture.call_args.args[0], 'thankyou_note_submitted')
        self.assertEqual(
            mock_capture.call_args.kwargs['properties']['form_type'],
            'donation_thank_you',
        )
        self.assertIsNone(mock_capture.call_args.kwargs['distinct_id'])

    @mock.patch('donations.signals.posthog_capture')
    def test_posthog_event_identifies_signed_in_submitter(self, mock_capture):
        account_uuid = "11111111-1111-1111-1111-111111111111"
        data = {
            "thank_you_note": "Thanks OpenStax!",
            "last_name": "Reed",
            "first_name": "Robin",
            "school": "Rice University",
            "source": "PDF download",
            "account_uuid": account_uuid,
        }
        response = self.client.post(
            '/apps/cms/api/donations/thankyounote/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            str(mock_capture.call_args.kwargs['distinct_id']), account_uuid
        )


class ThankYouNoteFieldFallbackTest(APITestCase, TestCase):
    """Stale cached SPA bundles post 'institution' instead of 'school' (Sentry OPENSTAX-CMS-WM)."""

    def test_accepts_legacy_institution_field(self):
        data = {"thank_you_note": "Thanks!", "first_name": "Francis", "last_name": "Martindale",
                "institution": "Open University", "source": "PDF download"}
        response = self.client.post('/apps/cms/api/donations/thankyounote/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ThankYouNote.objects.get(last_name='Martindale').institution, 'Open University')

    def test_missing_optional_fields_do_not_error(self):
        response = self.client.post('/apps/cms/api/donations/thankyounote/', {"thank_you_note": "Thanks!"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ThankYouNote.objects.get(thank_you_note='Thanks!').institution, '')

    def test_missing_note_returns_400(self):
        response = self.client.post('/apps/cms/api/donations/thankyounote/', {"first_name": "Bot"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ThankYouNote.objects.exists())
