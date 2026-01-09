from django.test import TestCase
from datetime import date, timedelta
from salesforce.models import School
from salesforce.serializers import SchoolSerializer

class SchoolResearchAgreementTest(TestCase):
    def test_research_agreement_active_within_range(self):
        today = date.today()
        school = School.objects.create(
            name="Test School",
            research_agreement_start_date=today - timedelta(days=10),
            research_agreement_end_date=today + timedelta(days=10)
        )
        serializer = SchoolSerializer(school)
        self.assertTrue(serializer.data['research_agreement_active'])

    def test_research_agreement_active_before_start(self):
        today = date.today()
        school = School.objects.create(
            name="Test School",
            research_agreement_start_date=today + timedelta(days=10),
            research_agreement_end_date=today + timedelta(days=20)
        )
        serializer = SchoolSerializer(school)
        self.assertFalse(serializer.data['research_agreement_active'])

    def test_research_agreement_active_after_end(self):
        today = date.today()
        school = School.objects.create(
            name="Test School",
            research_agreement_start_date=today - timedelta(days=20),
            research_agreement_end_date=today - timedelta(days=10)
        )
        serializer = SchoolSerializer(school)
        self.assertFalse(serializer.data['research_agreement_active'])

    def test_research_agreement_active_no_dates(self):
        school = School.objects.create(
            name="Test School"
        )
        serializer = SchoolSerializer(school)
        self.assertFalse(serializer.data['research_agreement_active'])

    def test_research_agreement_active_start_date_today(self):
        today = date.today()
        school = School.objects.create(
            name="Test School",
            research_agreement_start_date=today,
            research_agreement_end_date=today + timedelta(days=10)
        )
        serializer = SchoolSerializer(school)
        self.assertTrue(serializer.data['research_agreement_active'])

    def test_research_agreement_active_end_date_today(self):
        today = date.today()
        school = School.objects.create(
            name="Test School",
            research_agreement_start_date=today - timedelta(days=10),
            research_agreement_end_date=today
        )
        serializer = SchoolSerializer(school)
        self.assertTrue(serializer.data['research_agreement_active'])
