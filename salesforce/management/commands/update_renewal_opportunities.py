import datetime
from django.core.management.base import BaseCommand
from salesforce.models import AdoptionOpportunityRecord, RenewalOpportunity
from salesforce.salesforce import Salesforce

class Command(BaseCommand):
    help = "update book adoptions from salesforce.com for getting adoptions by account id"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            now = datetime.datetime.now()
            renewal_date = datetime.date(now.year - 1, now.month, now.day)
            renewal_date_str = renewal_date.strftime('%Y-%m-%d')
            print('***renewal date: ' + str(renewal_date_str))

            command = "Select Id, Accounts_UUID__c, Book__c.Name, Fall_Students__c, Spring_Students__c, Renewal_Date__c from Opportunities where Renewal_Date__c > {} AND Accounts_UUID__c != null AND Type = 'Renewal'".format(renewal_date_str)
        #Book__r.Name( or maybe
        #Book__c.Name -
        #try to avoid using Book_Name__c),
        #Fall_Students__c, Spring_Students__c (most recent number from either of these fields)
        #WHERE Renewal_Date__c > 6 / 1 / 2021 ( or maybe > 1 year)
        #FROM Opportunities
            response = sf.query_all(command)
            records = response['records']
            print('num of records: ' + str(records.size))

            for record in records:
                renewal = RenewalOpportunity.objects.update_or_create(opportunity_id=record['Id'])
                renewal.account_uuid = record['Accounts_UUID__c']
                renewal.book_name = record['Book__c.Name']
                renewal.fall_student_number = record['Fall_Students__c']
                renewal.spring_student_number = record['Spring_Students__c']
                renewal.renewal_date = record['Renewal_Date__c']

                renewal.save()

