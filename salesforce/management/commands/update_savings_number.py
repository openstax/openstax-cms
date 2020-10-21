from django.core.management.base import BaseCommand
from books.models import Book
from salesforce.salesforce import Salesforce

class Command(BaseCommand):
    help = "update savings numbers from Salesforce"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            books = Book.objects.all()

            adoption_query = "SELECT Book__r.Name, Count(Id) FROM Adoption__c GROUP BY Book__r.Name"
            adoption_response = sf.query_all(adoption_query)

            savings_query = "SELECT Book__r.Name, SUM(Yearly_Savings__c) FROM Opportunity WHERE IsWon=True GROUP BY Book__r.Name"
            savings_response = sf.query_all(savings_query)


            for book in books:
                print(book.title)
                for record in adoption_response['records']:
                    if record['Name'] == book.salesforce_name:
                        book.adoptions = int(record['expr0'])

                for record in savings_response['records']:
                    if record['Name'] == book.salesforce_name:
                        book.savings = format(record['expr0'], '.2f')

                book.save()


            response = self.style.SUCCESS("Updating savings numbers complete!")
        self.stdout.write(response)
