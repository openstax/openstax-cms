from django.core.management.base import BaseCommand
from django.db import transaction
from books.models import Book
from salesforce.models import SavingsNumber
from salesforce.salesforce import Salesforce

class Command(BaseCommand):
    help = "update savings numbers from Salesforce"

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
            savings_number = int(response['records'][0]['expr0'])
            sf_data.savings = savings_number

            sf_data.save()


            # Book specific updates
            books = Book.objects.all()
            adoption_query = "SELECT Book__r.Name, Count(Id) FROM Adoption__c GROUP BY Book__r.Name"
            adoption_response = sf.query_all(adoption_query)

            savings_query = "SELECT Book__r.Name, SUM(Yearly_Savings__c) FROM Opportunity WHERE IsWon=True GROUP BY Book__r.Name"
            savings_response = sf.query_all(savings_query)


            for book in books:
                for record in adoption_response['records']:
                    if record['Name'] == book.salesforce_name:
                        book.adoptions = int(record['expr0'])

                for record in savings_response['records']:
                    if record['Name'] == book.salesforce_name:
                        book.savings = int(record['expr0'])

                with transaction.atomic():
                    book.save()


            response = self.style.SUCCESS("Updating savings numbers complete!")
        self.stdout.write(response)
