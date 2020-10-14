from django.core.management.base import BaseCommand
from salesforce.models import SavingsNumber
from salesforce.salesforce import Salesforce
from pprint import pprint

class Command(BaseCommand):
    help = "update schools from salesforce.com"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            try:
                sf_data = SavingsNumber.objects.latest('updated')
            except SavingsNumber.DoesNotExist:
                sf_data = SavingsNumber()

            adoption_query = "SELECT COUNT(Id) FROM Adoption__c"
            response = sf.query_all(adoption_query)
            adoption_number = int(response['records'][0]['expr0'])
            sf_data.adoptions_count = adoption_number


            savings_query = "Select SUM(All_Time_Savings2__c) FROM Account"
            response = sf.query_all(savings_query)
            savings_number = float(response['records'][0]['expr0'])
            sf_data.savings = savings_number


            sf_data.save()
            response = self.style.SUCCESS("Updating savings numbers complete!")
        self.stdout.write(response)
