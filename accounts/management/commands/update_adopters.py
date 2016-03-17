from django.core.management.base import BaseCommand, CommandError
from accounts.salesforce import Salesforce
from adopters.models import Adopter
from pages.models import AdoptersPage

class Command(BaseCommand):
    help = "update adopters from salesforce.com"

    def handle(self, *args, **options):
        if AdoptersPage.objects.exists():
            adopter_page = AdoptersPage.objects.all()[0]
            
            with Salesforce() as sf:
                salesforce_adopters_list = sf.adopters()
                for salesforce_adopter in salesforce_adopters_list:
                    adopter, created = Adopter.objects.get_or_create(salesforce_id=salesforce_adopter['Id'],
                                                                     name=salesforce_adopter['Name'],
                                                                     description=salesforce_adopter['Description'],
                                                                     website=salesforce_adopter['Website'],
                                                                     page_id=adopter_page.pk,)
                    adopter.save()
            responce = self.style.SUCCESS("Successfully updated adopters")
        else: 
            response = self.style.HTTP_NOT_FOUND("Adopters page does not exist")
        self.stdout.write(responce)
