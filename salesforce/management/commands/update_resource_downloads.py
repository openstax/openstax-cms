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
            new_data = []
            update_data = []
            for nrd in new_resource_downloads:
                if not nrd.salesforce_id:
                    data_dict_item = {'Contact__c': nrd.contact_id,
                                      'Last_accessed__c': nrd.last_access.strftime('%Y-%m-%d'),
                                      'Name': nrd.resource_name,
                                      'Book__c': nrd.book.salesforce_abbreviation,
                                      'Book_Format__c': nrd.book_format,
                                      'Number_of_times_accessed__c': nrd.number_of_times_accessed,
                                      'Accounts_UUID__c': str(nrd.account_uuid)}
                    new_data.append(data_dict_item)
                else:
                    data_dict_item = { 'Id': nrd.salesforce_id,
                                       'Last_Resource_Download_Date__c': nrd.last_access.strftime('%Y-%m-%d'),
                                       'Number_of_times_accessed__c': nrd.number_of_times_accessed }
                    update_data.append(data_dict_item)

            new_results = sf.bulk.Resource__c.insert(new_data)
            upsert_results = sf.bulk.Resource__c.update(update_data)


            response = self.style.SUCCESS("[SF Resource Download] Failed: {}.".format(num_failed))
            self.stdout.write(response)
