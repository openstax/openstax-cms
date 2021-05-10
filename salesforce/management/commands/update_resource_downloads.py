from django.core.management.base import BaseCommand
from django.db import transaction
from salesforce.models import ResourceDownload
from salesforce.salesforce import Salesforce
from datetime import timedelta, date

class Command(BaseCommand):
    help = "update resource download records with SF"

    def handle(self, *args, **options):
        yesterday = date.today() - timedelta(days=1)
        new_resource_downloads = ResourceDownload.objects.filter(last_access=yesterday).distinct()

        with Salesforce() as sf:
            data = []
            for nrd in new_resource_downloads:
                contact = sf.Contact.get(nrd.contact_id)
                data_dict_item = { 'Id': nrd.contact_id, 'Last_Resource_Download_Date__c': nrd.last_access.strftime('%Y-%m-%d')}
                data.append(data_dict_item)

            results = sf.bulk.Contact.update(data)
            num_updated = 0
            num_failed = 0
            for result in results:
                if result['success']:
                    num_updated += 1
                else:
                    num_failed += 1

            response = self.style.SUCCESS("[SF Resource Download] Updated {} Failed {}.".format(num_updated, num_failed))
            self.stdout.write(response)
