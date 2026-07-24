"""PartnersPage's category_mapping/field_name_mapping/partner_type_choices are
thin delegators to salesforce.partner_filters - see salesforce/test_partner_filters.py
for the actual derivation logic tests."""
from django.test import TestCase

from pages.models.partners import PartnersPage
from salesforce import partner_filters
from salesforce.models import Partner


class PartnersPageDelegationTests(TestCase):
    def setUp(self):
        Partner.objects.create(
            partner_name="Acme", visible_on_website=True,
            adaptivity_adaptive_presentation=True, partner_type="AI")

    def test_category_mapping_matches_partner_filters(self):
        self.assertEqual(PartnersPage.category_mapping(), partner_filters.category_mapping())

    def test_field_name_mapping_matches_partner_filters(self):
        self.assertEqual(PartnersPage.field_name_mapping(), partner_filters.field_name_mapping())

    def test_partner_type_choices_matches_partner_filters(self):
        self.assertEqual(PartnersPage.partner_type_choices(), partner_filters.partner_type_choices())
