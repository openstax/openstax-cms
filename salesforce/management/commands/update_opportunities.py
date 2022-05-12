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

            #first, we need to upload any records that have been updated
            # adoptions_num_updated = 0
            #
            # adoptions = AdoptionOpportunityRecord.objects.filter(verified=True)
            # data = []
            # for adoption in adoptions:
            #     data_dict_item = {
            #         'Id': adoption.opportunity_id,
            #         'CloseDate': adoption.last_update.strftime('%Y-%m-%d'),
            #         'Type': 'Renewal - Verified'
            #     }
            #     data.append(data_dict_item)
            # results = sf.bulk.Opportunity.update(data)
            # for result in results:
            #     if result['success']: # we don't need to store these anymore, they are in SF now with a new opportunity type (so we don't get them in the next step)
            #         adoptions_num_updated = adoptions_num_updated + 1
            #         adoptions.get(opportunity_id=result['id']).delete()


            # then we will get any new records
            command = "SELECT Id, Accounts_UUID__c, Book_Text__c, Contact_Email__c, School_Name__c, Yearly_Students__c, Students__c, Type, Base_Year__c, IsWon, Fall_Students__c, Spring_Students__c, Summer_Students__c from Opportunity WHERE Accounts_UUID__c != null AND Type = 'Renewal' AND Base_Year__c = {} AND IsWon = True".format(year)

            response = sf.query_all(command)
            records = response['records']

            num_created = 0
            num_updated = 0
            for record in records:
                opportunity, created = AdoptionOpportunityRecord.objects.update_or_create(
                    opportunity_id=record['Id'],
                    defaults = {'account_uuid': record['Accounts_UUID__c'],
                                'book_name': record['Book_Text__c'],
                                'email': record['Contact_Email__c'],
                                'school': record['School_Name__c'],
                                'yearly_students': record['Yearly_Students__c'],
                                'fall_student_number': record['Fall_Students__c'],
                                'spring_student_number': record['Spring_Students__c'],
                                'summer_student_number': record['Summer_Students__c'],
                                }
                    )
                opportunity.save()
                if created:
                    num_created = num_created + 1
                else:
                    num_updated = num_updated + 1

            response = self.style.SUCCESS("Successfully updated opportunity records. {} were newly created and {} were updated.".format(num_created, num_updated))
        self.stdout.write(response)
