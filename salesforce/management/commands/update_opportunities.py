import datetime
import uuid
from django.core.management.base import BaseCommand
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

    def process_results(self, results, delete_stale=False):
        for i, record in enumerate(results):
            # they have newer records than last year, delete all previous records for this user
            if delete_stale:
                adoptions = AdoptionOpportunityRecord.objects.filter(account_uuid=record['Opportunity__r']['Contact__r']['Accounts_UUID__c']).last()
                if adoptions:
                    if adoptions.created.date() < datetime.date.today():
                        AdoptionOpportunityRecord.objects.filter(account_uuid=record['Opportunity__r']['Contact__r']['Accounts_UUID__c']).delete()

            try:
                # don't build records for non-active books
                if record['Opportunity__r']['Book__r']['Active__c']:
                    opportunity, created = AdoptionOpportunityRecord.objects.update_or_create(
                        opportunity_id=[record['Id']],
                        account_uuid=uuid.UUID(record['Opportunity__r']['Contact__r']['Accounts_UUID__c']),
                        book_name=record['Opportunity__r']['Book__r']['Name'],
                        defaults={'opportunity_stage': record['Opportunity__r']['StageName'],
                                  'adoption_type': record['Adoption_Type__c'],
                                  'base_year': record['Base_Year__c'],
                                  'confirmation_date': record['Confirmation_Date__c'],
                                  'confirmation_type': record['Confirmation_Type__c'],
                                  'how_using': record['How_Using__c'],
                                  'savings': record['Savings__c'],
                                  'students': record['Students__c']
                                  }
                    )
                    opportunity.save()
            except ValueError:
                sentry_sdk.capture_message("Adoption {} has a badly formatted Account UUID: {}".format(record['Id'], record['Opportunity__r']['Contact__r']['Accounts_UUID__c']))
            except TypeError:
                sentry_sdk.capture_message("Adoption {} exists without a book".format(record['Id']))

    @monitor(monitor_slug='update-opportunities')
    def handle(self, *args, **options):
        with Salesforce() as sf:
            now = datetime.datetime.now()

            base_year = now.year
            if now.month < 7:  # before july, current year minus 2 (4/1/2024, base year = 2023)
                base_year -= 2
            else:  # otherwise, current year minus 1 (10/1/2024, base year = 2023)
                base_year -= 1

            # first, we get last year's records
            # these people need to renew, show them what we know from last base year confirmed adoption
            query = self.query_base_year(base_year, "Past Adopter")

            results = sf.bulk.Adoption__c.query(query)
            self.process_results(results)

            # now get this year's records - this will ensure accurate data on the renewal form if already filled out
            current_base_year = base_year + 1
            updated_records = self.query_base_year(current_base_year, "Current Adopter")

            results = sf.bulk.Adoption__c.query(updated_records)
            self.process_results(results, delete_stale=True)

            invalidate_cloudfront_caches('salesforce/renewal')

