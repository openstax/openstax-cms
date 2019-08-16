import datetime
from django.core.management.base import BaseCommand
from salesforce.models import AdoptionOpportunityRecord
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "update book adoptions from salesforce.com for use on the renewal form"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            now = datetime.datetime.now()
            year = now.year
            if now.month < 7: # Salesforce needs the school base year, this is how they calculate it
                year = year - 1

            command = "SELECT Id, OS_Accounts_ID__c, Book_Text__c, Contact_Email__c, School_Name__c, Yearly_Students__c, Type, Base_Year__c, IsWon from Opportunity WHERE OS_Accounts_ID__c != null AND Type = 'Renewal' AND Base_Year__c = {} AND IsWon = True".format(year)
            # Type = 'Renewal' <-- this will need to be changed for QA testing each time (New Business is for brand new adoptions)

            response = sf.query_all(command)
            records = response['records']

            if records:
                AdoptionOpportunityRecord.objects.all().delete()

            num_created = 0
            for record in records:

                opportunity, created = AdoptionOpportunityRecord.objects.update_or_create(
                    opportunity_id=record['Id'],
                    defaults={'account_id': record['OS_Accounts_ID__c'],
                              'book_name': record['Book_Text__c'],
                              'email': record['Contact_Email__c'],
                              'school': record['School_Name__c'],
                              'yearly_students': record['Yearly_Students__c']
                              },
                )

                if created:
                    num_created = num_created + 1

                opportunity.save()

            response = self.style.SUCCESS("Successfully updated opportunity records. {} were newly created.".format(num_created))
        self.stdout.write(response)
