import datetime
import uuid
from django.core.management.base import BaseCommand
from django.db import transaction
from salesforce.models import AdoptionOpportunityRecord
from salesforce.salesforce import Salesforce
from global_settings.functions import invalidate_cloudfront_caches
import sentry_sdk
from sentry_sdk.crons import monitor


class Command(BaseCommand):
    help = "update book adoptions from salesforce.com for getting adoptions by account uuid"

    def query_base_year(self, base_year, adoption_status):
        query = ("SELECT Id, "
                 "Adoption_Type__c, "
                 "Base_Year__c, "
                 "Confirmation_Date__c, "
                 "Confirmation_Type__c, "
                 "How_Using__c, "
                 "Savings__c, "
                 "Students__c, "
                 "Opportunity__r.Book__r.Name, "
                 "Opportunity__r.Book__r.Active__c, "
                 "Opportunity__r.StageName, "
                 "Opportunity__r.Contact__r.Accounts_UUID__c "
                 "FROM Adoption__c WHERE "
                 "Base_Year__c = {} AND Opportunity__r.Contact__r.Accounts_UUID__c  != null "
                 "AND Confirmation_Type__c = 'OpenStax Confirmed Adoption' "
                 "AND Opportunity__r.Contact__r.Adoption_Status__c = '{}'").format(base_year, adoption_status)

        return query

    def account_uuid(self, record):
        """Return the parsed Accounts UUID for a Salesforce adoption record.

        Returns None (and reports to Sentry) when the UUID is missing or
        malformed so the caller can skip the record instead of crashing.
        """
        raw = record['Opportunity__r']['Contact__r']['Accounts_UUID__c']
        try:
            return uuid.UUID(raw)
        except (ValueError, TypeError):
            sentry_sdk.capture_message(
                "Adoption {} has a badly formatted Account UUID: {}".format(record['Id'], raw)
            )
            return None

    def process_results(self, results):
        for record in results:
            try:
                # don't build records for non-active books
                if not record['Opportunity__r']['Book__r']['Active__c']:
                    continue
            except (TypeError, KeyError):
                sentry_sdk.capture_message("Adoption {} exists without a book".format(record['Id']))
                continue

            account_uuid = self.account_uuid(record)
            if account_uuid is None:
                continue

            # opportunity_id is the unique key (one row per Salesforce Adoption record).
            # Everything else is an attribute that can change between syncs, so it lives
            # in defaults and gets updated in place rather than driving the lookup.
            AdoptionOpportunityRecord.objects.update_or_create(
                opportunity_id=record['Id'],
                defaults={
                    'account_uuid': account_uuid,
                    'book_name': record['Opportunity__r']['Book__r']['Name'],
                    'opportunity_stage': record['Opportunity__r']['StageName'],
                    'adoption_type': record['Adoption_Type__c'],
                    'base_year': record['Base_Year__c'],
                    'confirmation_date': record['Confirmation_Date__c'],
                    'confirmation_type': record['Confirmation_Type__c'],
                    'how_using': record['How_Using__c'],
                    'savings': record['Savings__c'],
                    'students': record['Students__c'],
                },
            )

    def current_adopter_uuids(self, results):
        """Collect the set of valid Account UUIDs present in this year's results."""
        uuids = set()
        for record in results:
            account_uuid = self.account_uuid(record)
            if account_uuid is not None:
                uuids.add(account_uuid)
        return uuids

    @monitor(monitor_slug='update-opportunities')
    def handle(self, *args, **options):
        with Salesforce() as sf:
            now = datetime.datetime.now()

            base_year = now.year
            if now.month < 7:  # before july, current year minus 2 (4/1/2024, base year = 2023)
                base_year -= 2
            else:  # otherwise, current year minus 1 (10/1/2024, base year = 2023)
                base_year -= 1

            # First, last year's confirmed adoptions for past adopters: these people
            # need to renew, so we surface what we know from last base year so the
            # frontend can show them the renewal nudge.
            past_adopters = sf.bulk.Adoption__c.query(
                self.query_base_year(base_year, "Past Adopter")
            )
            with transaction.atomic():
                self.process_results(past_adopters)

            # Now this year's confirmed adoptions for current adopters. They have
            # already confirmed for the current base year, so replace last year's
            # nudge data with the accurate current-year records. We clear every
            # current adopter's existing rows once, in bulk, then upsert.
            current_base_year = base_year + 1
            current_adopters = sf.bulk.Adoption__c.query(
                self.query_base_year(current_base_year, "Current Adopter")
            )
            with transaction.atomic():
                stale_accounts = self.current_adopter_uuids(current_adopters)
                AdoptionOpportunityRecord.objects.filter(
                    account_uuid__in=stale_accounts
                ).delete()
                self.process_results(current_adopters)

            invalidate_cloudfront_caches('salesforce/renewal')
