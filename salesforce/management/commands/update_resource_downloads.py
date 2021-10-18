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
        num_updated = 0
        num_failed = 0

        upload_from_date = timezone.now() - timedelta(days=options['days_to_upload'])
        new_resource_downloads = ResourceDownload.objects.filter(last_access__gte=upload_from_date)

        self.stdout.write(self.style.WARNING("Uploading records from {} to today".format(upload_from_date.strftime("%m/%d/%Y"))))
        self.stdout.write(self.style.WARNING("Found {} records. Uploading to Salesforce...".format(new_resource_downloads.count())))

        with Salesforce() as sf:
            data = []
            for nrd in new_resource_downloads:
                try:
                    contact = sf.Contact.get(nrd.contact_id)
                    data_dict_item = { 'Id': nrd.salesforce_id,
                                       'Contact__c': nrd.contact_id,
                                       'Last_Resource_Download_Date__c': nrd.last_access.strftime('%Y-%m-%d'),
                                       'Accounts_UUID__c': nrd.account_uuid,
                                       'Name': nrd.resource_name,
                                       'Book__c': nrd.book.salesforce_name,
                                       'Book_Format__c': nrd.book_format,
                                       'Number_of_times_accessed__c': nrd.number_of_times_accessed }
                    data.append(data_dict_item)
                except SalesforceResourceNotFound:
                    num_failed += 1
                    self.stdout.write(self.style.ERROR("Contact Id not found: {}".format(nrd.contact_id)))

            results = sf.bulk.Contact.upsert(data, 'Id', batch_size=10000, use_serial=True)
            for result in results:
                if result['success']:
                    num_updated += 1
                else:
                    num_failed += 1

            response = self.style.SUCCESS("[SF Resource Download] Updated {} Failed {}.".format(num_updated, num_failed))
            self.stdout.write(response)
