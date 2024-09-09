from django.core.management.base import BaseCommand
from salesforce.models import ResourceDownload
from salesforce.salesforce import Salesforce
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "update resource download records with SF"

    def add_arguments(self, parser):
        parser.add_argument('--days_to_upload', nargs='?', default=1, type=int)

    def handle(self, *args, **options):
        upload_from_date = timezone.now() - timedelta(days=options['days_to_upload'])
        new_resource_downloads = ResourceDownload.objects.filter(last_access__gte=upload_from_date)

        self.stdout.write(self.style.WARNING("Uploading records from {} to today".format(upload_from_date.strftime("%m/%d/%Y"))))
        self.stdout.write(self.style.WARNING("Found {} records. Uploading to Salesforce...".format(new_resource_downloads.count())))

        with Salesforce() as sf:
            new_data = []
            for nrd in new_resource_downloads:
                if nrd.book:
                    data_dict_item = {'Contact__c': nrd.contact_id,
                                      'Last_accessed__c': nrd.last_access.strftime('%Y-%m-%d'),
                                      'Name': nrd.resource_name,
                                      'Book__c': nrd.book.salesforce_abbreviation,
                                      'Book_Format__c': nrd.book_format,
                                      'Accounts_UUID__c': str(nrd.account_uuid)}
                    new_data.append(data_dict_item)

            if len(new_data) > 0:
                new_results = sf.bulk.Resource__c.insert(new_data)

            response = self.style.SUCCESS("SF Resource Download Completed. Sent: {}.".format(len(new_data)))
            self.stdout.write(response)
