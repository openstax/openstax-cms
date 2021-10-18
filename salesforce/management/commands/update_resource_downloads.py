from django.core.management.base import BaseCommand
from django.db import transaction
from salesforce.models import ResourceDownload
from salesforce.salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceResourceNotFound
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "update resource download records with SF"

    def add_arguments(self, parser):
        parser.add_argument('--days_to_upload', nargs='?', default=1, type=int)

    def handle(self, *args, **options):
        upload_from_date = timezone.now() - timedelta(days=options['days_to_upload'])
        new_resource_downloads = ResourceDownload.objects.filter(last_access__gte=upload_from_date).distinct()

        self.stdout.write(self.style.WARNING("Uploading records from {} to today".format(upload_from_date.strftime("%m/%d/%Y"))))
        self.stdout.write(self.style.WARNING("Found {} records. Uploading to Salesforce...".format(new_resource_downloads.count())))

        with Salesforce() as sf:
            data = []
            for nrd in new_resource_downloads:
                try:
                    contact = sf.Contact.get(nrd.contact_id)
                    data_dict_item = { 'Id': nrd.contact_id, 'Last_Resource_Download_Date__c': nrd.last_access.strftime('%Y-%m-%d')}
                    data.append(data_dict_item)
                except SalesforceResourceNotFound:
                    self.stdout.write(self.style.ERROR("Contact Id not found: {}".format(nrd.contact_id)))

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
