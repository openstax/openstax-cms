from django.core.management.base import BaseCommand
from salesforce.models import Adopter
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "update adopters from salesforce.com"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            command = "SELECT Id, Name, Description, Website FROM Account "\
                          "WHERE Number_of_Adoptions__c > 0 and Id != '001U0000011KxWa'"
            response = sf.query_all(command)
            sf_adopters = response['records']

            if sf_adopters:
                Adopter.objects.all().delete()

            for sf_adopter in sf_adopters:

                adopter, created = Adopter.objects.update_or_create(
                    sales_id=sf_adopter['Id'],
                    defaults={'name': sf_adopter['Name'],
                              'description': sf_adopter['Description'],
                              'website': sf_adopter['Website'],
                              },
                )

                adopter.save()
            response = self.style.SUCCESS("Successfully updated adopters")
        self.stdout.write(response)
