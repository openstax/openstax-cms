"""Tests for the static partner filter registry (see partner_filters.py) -
category_mapping/field_name_mapping/partner_type_choices are derived live from
real Partner rows plus PARTNER_FILTER_CATEGORIES, with no DB-backed mapping
tables to keep in sync."""
from django.test import TestCase

from salesforce import partner_filters
from salesforce.models import Partner


class CategoryMappingTests(TestCase):
    def test_category_appears_when_a_visible_partner_uses_one_of_its_fields(self):
        Partner.objects.create(
            partner_name="Acme", visible_on_website=True,
            adaptivity_adaptive_presentation=True)

        self.assertEqual(partner_filters.category_mapping().get("Adaptivity"), "adaptivity_")

    def test_category_absent_when_no_visible_partner_uses_any_of_its_fields(self):
        Partner.objects.create(
            partner_name="Acme", visible_on_website=True,
            adaptivity_adaptive_presentation=False)

        self.assertNotIn("Adaptivity", partner_filters.category_mapping())

    def test_hidden_partner_does_not_count(self):
        Partner.objects.create(
            partner_name="Acme", visible_on_website=False,
            adaptivity_adaptive_presentation=True)

        self.assertNotIn("Adaptivity", partner_filters.category_mapping())

    def test_cost_category_always_present(self):
        # affordability_cost is in ALWAYS_VISIBLE_FIELDS regardless of any partner data.
        self.assertEqual(partner_filters.category_mapping().get("Cost"), "affordability_")


class FieldNameMappingTests(TestCase):
    def test_field_appears_with_its_configured_label(self):
        Partner.objects.create(
            partner_name="Acme", visible_on_website=True, LMS_SSO=True)

        mapping = partner_filters.field_name_mapping()
        self.assertEqual(
            mapping.get("Single sign-on (Lets students log in with their college account information)"),
            "LMS_SSO",
        )

    def test_field_absent_when_unused(self):
        Partner.objects.create(partner_name="Acme", visible_on_website=True)
        mapping = partner_filters.field_name_mapping()
        self.assertNotIn("LMS_SSO", mapping.values())

    def test_assignment_outside_resources_grouped_under_assignment_management(self):
        # Regression check for the pre-existing typo bug (assigment_outside_resources)
        # that silently kept this field out of Assignment Management on the live site.
        Partner.objects.create(
            partner_name="Acme", visible_on_website=True, assignment_outside_resources=True)

        self.assertIn("assignment_outside_resources", partner_filters.field_name_mapping().values())
        self.assertEqual(partner_filters.category_mapping().get("Assignment Management"), "assignment_")

    def test_affordability_cost_always_included_even_with_no_data(self):
        Partner.objects.create(partner_name="Acme", visible_on_website=True)
        self.assertIn("affordability_cost", partner_filters.field_name_mapping().values())


class PartnerTypeChoicesTests(TestCase):
    def test_returns_distinct_sorted_visible_partner_types(self):
        Partner.objects.create(partner_name="A", visible_on_website=True, partner_type="Videos")
        Partner.objects.create(partner_name="B", visible_on_website=True, partner_type="AI")
        Partner.objects.create(partner_name="C", visible_on_website=True, partner_type="AI")

        self.assertEqual(partner_filters.partner_type_choices(), ["AI", "Videos"])

    def test_excludes_hidden_partners_and_blank_types(self):
        Partner.objects.create(partner_name="A", visible_on_website=False, partner_type="Videos")
        Partner.objects.create(partner_name="B", visible_on_website=True, partner_type="")
        Partner.objects.create(partner_name="C", visible_on_website=True, partner_type=None)

        self.assertEqual(partner_filters.partner_type_choices(), [])
