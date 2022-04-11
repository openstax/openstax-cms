from django.core.management.base import BaseCommand
from salesforce.models import Partner
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "update partners with new partner object ids"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            query = "SELECT " \
                    "Id, " \
                    "Name " \
                    "FROM Partner__c"
            response = sf.query_all(query)
            sf_partners = response['records']

        processed_partners = 0
        for partner in sf_partners:
            try:
                p = Partner.objects.get(partner_name=partner['Name'])
                p.salesforce_id = partner['Id']
                p.save()
                processed_partners += 1
            except:
                continue

        response = self.style.SUCCESS("Successfully updated {} partners.".format(processed_partners))
        self.stdout.write(response)


