import datetime
import uuid
from django.core.management.base import BaseCommand
from salesforce.models import AdoptionOpportunityRecord
from salesforce.salesforce import Salesforce
import sentry_sdk

class Command(BaseCommand):
    help = "update book adoptions from salesforce.com for getting adoptions by account uuid"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            now = datetime.datetime.now()

            base_year = now.year
            if now.month < 7:  # if it's before July, the base year is the previous year (4/1/2024 = base_year 2023)
                base_year -= 2
            else:
                base_year -= 1

            # TODO: I don't think this is needed - updating the records should be fine, and keeps something on the form
            # TODO: for the user. Eventually, this should update CMS DB with updated data if they fill out the form
            # truncate the table
            # AdoptionOpportunityRecord.objects.all().delete()

            # then we will get any new records
            query = ("SELECT Id, "
                     "Adoption_Type__c, "
                     "Base_Year__c, "
                     "Confirmation_Date__c, "
                     "Confirmation_Type__c, "
                     "How_Using__c, "
                     "Savings__c, "
                     "Students__c, "
                     "Opportunity__r.Book__r.Name, "
                     "Opportunity__r.StageName, "
                     "Opportunity__r.Contact__r.Accounts_UUID__c "
                     "FROM Adoption__c WHERE "
                     "Base_Year__c = {} AND Opportunity__r.Contact__r.Accounts_UUID__c  != null "
                     "AND Confirmation_Type__c = 'OpenStax Confirmed Adoption' "
                     "AND Opportunity__r.Contact__r.Adoption_Status__c != 'Current Adopter'").format(base_year)

            # This generally returns more than 2,000 records (the SF limit)
            # See simplate_salesforce documentation for bulk queries: https://github.com/simple-salesforce/simple-salesforce?tab=readme-ov-file#using-bulk
            results = sf.bulk.Adoption__c.query(query)

            # TODO: this doesn't need to be updating on the opp id, the info never changes
            for i, record in enumerate(results):
                try:
                    opportunity, created = AdoptionOpportunityRecord.objects.update_or_create(
                        account_uuid=uuid.UUID(record['Opportunity__r']['Contact__r']['Accounts_UUID__c']),
                        book_name=record['Opportunity__r']['Book__r']['Name'],
                        defaults={'opportunity_id': record['Id'],
                                  'opportunity_stage': record['Opportunity__r']['StageName'],
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

                # TODO: need to grab current adoptions and if the info has changed, update it so the user sees most recent adoption info
                # re-submitting the form will update the current year adoption numbers, which the user might not expect
