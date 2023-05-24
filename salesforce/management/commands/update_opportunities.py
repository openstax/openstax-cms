import datetime
from django.core.management.base import BaseCommand
from salesforce.models import AdoptionOpportunityRecord
from salesforce.salesforce import Salesforce

class Command(BaseCommand):
    help = "update book adoptions from salesforce.com for getting adoptions by account uuid"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            now = datetime.datetime.now()

            year = now.year
            if now.month < 7: # Salesforce needs the school base year, this is how they calculate it
                year = year - 1


            # truncate the table
            AdoptionOpportunityRecord.objects.all().delete()

            # then we will get any new records
            command = "SELECT Id, Contact__r.Accounts_UUID__c, Book__r.Name, Base_Year__c, IsWon, Fall_Students__c, Spring_Students__c, Summer_Students__c from Opportunity WHERE Contact__r.Accounts_UUID__c != null AND Base_Year__c = {} AND IsWon = True".format(year)

            response = sf.query_all(command)
            records = response['records']

            num_created = 0
            for record in records:
                opportunity, created = AdoptionOpportunityRecord.objects.update_or_create(
                    opportunity_id=record['Id'],
                    defaults = {'account_uuid': record['Contact__r']['Accounts_UUID__c'],
                                'book_name': record['Book__r']['Name'],
                                'fall_student_number': record['Fall_Students__c'],
                                'spring_student_number': record['Spring_Students__c'],
                                'summer_student_number': record['Summer_Students__c'],
                                }
                    )
                opportunity.save()
                if created:
                    num_created = num_created + 1

            response = self.style.SUCCESS("Successfully updated opportunity records. {} were newly created.".format(num_created))
        self.stdout.write(response)
