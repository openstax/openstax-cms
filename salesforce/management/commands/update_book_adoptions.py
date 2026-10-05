import datetime

from django.core.management.base import BaseCommand
from sentry_sdk.crons import monitor

from books.models import Book
from global_settings.functions import invalidate_cloudfront_caches
from salesforce.models import SavingsNumber
from salesforce.salesforce import Salesforce
from salesforce.school_year import school_year_base_year

# 'User Behavior Informed Adoption' is modeled, not confirmed, so it stays out of the public count.
QUERY = (
    "SELECT Opportunity__r.Book__r.Name name, Opportunity__r.Book__r.Official_Name__c official_name, "
    "COUNT(Id) adoptions, SUM(Savings__c) savings "
    "FROM Adoption__c "
    "WHERE Base_Year__c = {base_year} "
    "AND Confirmation_Type__c IN ('OpenStax Confirmed Adoption', 'Third Party Confirmed Adoption') "
    "GROUP BY Opportunity__r.Book__r.Name, Opportunity__r.Book__r.Official_Name__c"
)


class Command(BaseCommand):
    help = "Sync each book's confirmed adoption and savings counts from Salesforce."

    def add_arguments(self, parser):
        parser.add_argument('--base-year', type=int, default=None,
                            help="School year base year (default: the current school year).")

    def totals_by_book_name(self, records):
        totals = {}
        for record in records:
            value = (record['adoptions'], record['savings'] or 0)
            for key in (record.get('name'), record.get('official_name')):
                if key:
                    totals[key] = value
        return totals

    @monitor(monitor_slug='update-book-adoptions')
    def handle(self, *args, **options):
        base_year = options['base_year'] or school_year_base_year(datetime.datetime.now().date())
        with Salesforce() as sf:
            records = sf.query_all(QUERY.format(base_year=base_year))['records']
        records = [r for r in records if r.get('name') or r.get('official_name')]
        totals = self.totals_by_book_name(records)

        matched = cleared = 0
        # queryset update() because Book.save() broadcasts fields to every Book and writes revisions
        for salesforce_name in Book.objects.order_by().values_list('salesforce_name', flat=True).distinct():
            if salesforce_name in totals:
                adoptions, savings = totals[salesforce_name]
                matched += Book.objects.filter(salesforce_name=salesforce_name).update(
                    adoptions=adoptions, savings=int(round(savings)))
            else:
                cleared += Book.objects.filter(salesforce_name=salesforce_name).update(
                    adoptions=None, savings=None)

        summary = SavingsNumber.objects.order_by('-updated').first() or SavingsNumber()
        summary.adoptions_count = sum(r['adoptions'] for r in records)
        summary.savings = int(round(sum(r['savings'] or 0 for r in records)))
        summary.save()

        invalidate_cloudfront_caches('books')
        self.stdout.write(self.style.SUCCESS(
            f"Base year {base_year}: {matched + cleared} books updated, {matched} matched, {cleared} cleared."))
