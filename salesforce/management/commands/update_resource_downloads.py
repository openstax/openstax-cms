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
        print(new_resource_downloads.count())

        with Salesforce() as sf:
            data = []
            for nrd in new_resource_downloads:
                print('*** contact_id: ' + nrd.contact_id + ' date: ' + nrd.last_access.strftime('%Y-%m-%d'))
                data_dict_item = { 'Id': nrd.contact_id, 'Last_Resource_Download_Date__c': nrd.last_access.strftime('%Y-%m-%d')}
                print('*** data_dict_item: ' + str(data_dict_item))
                data.append(data_dict_item)
            sf.bulk.Contact.update(data)

        response = self.style.SUCCESS("[SF Resource Download] Updated {}.".format(new_resource_downloads.count(),))
        self.stdout.write(response)
