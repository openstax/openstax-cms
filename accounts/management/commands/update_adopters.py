from django.core.management.base import BaseCommand, CommandError
from accounts.salesforce import Salesforce
from pages.models import Organizations


class Command(BaseCommand):
    help = "update adopters from salesforce.com"

    def add_arguments(self, parser):
        parser.add_argument('page_id', type=int)

    def handle(self, *args, **options):
        with Salesforce() as sf:
            salesforce_adopters_list = sf.adopters()
            for salesforce_adopter in salesforce_adopters_list:
                # FIXME: Organizations.objects.get_or_create
                if not Organizations.objects.filter(salesforce_id=salesforce_adopter['Id']):
                    new_cms_adopter = Organizations(salesforce_id=salesforce_adopter['Id'],
                                                    organization_name=salesforce_adopter[
                                                        'Name'],
                                                    description=salesforce_adopter[
                                                        'Description'],
                                                    website=salesforce_adopter[
                                                        'Website'],
                                                    page_id=options['page_id'],)
                    new_cms_adopter.save()
        success = self.style.SUCCESS("Successfully updated adopters")
        self.stdout.write(success)
