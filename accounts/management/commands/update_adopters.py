from django.core.management.base import BaseCommand, CommandError
from accounts.salesforce import Salesforce
from adopters.models import Adopter


class Command(BaseCommand):
    help = "update adopters from salesforce.com"

    def add_arguments(self, parser):
        parser.add_argument('page_id', type=int)

    def handle(self, *args, **options):
        with Salesforce() as sf:
            salesforce_adopters_list = sf.adopters()
            for salesforce_adopter in salesforce_adopters_list:
                adopter, created = Adopter.objects.get_or_create(salesforce_id=salesforce_adopter['Id'],
                                                                  name=salesforce_adopter['Name'],
                                                                  description=salesforce_adopter['Description'],
                                                                  website=salesforce_adopter['Website'],
                                                                  page_id=options['page_id'],)
                adopter.save() 
        success = self.style.SUCCESS("Successfully updated adopters")
        self.stdout.write(success)
