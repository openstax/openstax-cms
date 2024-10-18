import datetime
from django.core.management.base import BaseCommand
from salesforce.models import AdoptionOpportunityRecord
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "update book adoptions from salesforce.com for getting adoptions by account uuid"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            now = datetime.datetime.now()

            base_year = now.year
            if now.month >= 7:  # Salesforce needs the school base year, this is how they calculate it
                base_year -= 1

            # truncate the table
            AdoptionOpportunityRecord.objects.all().delete()

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
                     "AND Opportunity__r.Contact__r.Adoption_Status__c != 'Current Adopter' LIMIT 100").format(base_year)

            response = sf.query(query)
            records = response['records']

            for record in records:
                opportunity, created = AdoptionOpportunityRecord.objects.update_or_create(
                    opportunity_id=record['Id'],
                    defaults={'account_uuid': record['Opportunity__r']['Contact__r']['Accounts_UUID__c'],
                              'opportunity_stage': record['Opportunity__r']['StageName'],
                              'adoption_type': record['Adoption_Type__c'],
                              'base_year': record['Base_Year__c'],
                              'confirmation_date': record['Confirmation_Date__c'],
                              'confirmation_type': record['Confirmation_Type__c'],
                              'how_using': record['How_Using__c'],
                              'savings': record['Savings__c'],
                              'students': record['Students__c'],
                              'book_name': record['Opportunity__r']['Book__r']['Name'],
                              }
                )
                opportunity.save()
