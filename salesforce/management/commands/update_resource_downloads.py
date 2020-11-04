from django.core.management.base import BaseCommand
from salesforce.models import ResourceDownload
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "update resource download records with SF"

    def handle(self, *args, **options):
        new_resource_downloads = ResourceDownload.objects.filter(salesforce_id__isnull=True) # ones to create
        existing_resource_downloads = ResourceDownload.objects.exclude(salesforce_id__isnull=True) #ones to update (this can be done in bulk)

        number_to_create = new_resource_downloads.count()
        number_to_update = existing_resource_downloads.count()
        number_created = 0
        number_updated = 0

        with Salesforce() as sf:
            data = []
            for rd in existing_resource_downloads:
                data_dict_item = {
                    'Id': rd.salesforce_id,
                    'Book__c': rd.book.title,
                    'Book_Format__c': rd.book_format,
                    'OS_Accounts_ID__c': rd.account_id,
                    'Name': rd.resource_name,
                    'Number_of_times_accessed__c': rd.number_of_times_accessed,
                    'Last_accessed__c': rd.last_access.strftime('%Y-%m-%d')
                }
                data.append(data_dict_item)
                number_updated = number_updated + 1
            sf.bulk.Resource__c.update(data)


            for rd in new_resource_downloads:
                sf_resource = sf.Resource__c.create({
                    'Book__c': rd.book.title,
                    'Book_Format__c': rd.book_format,
                    'OS_Accounts_ID__c': rd.account_id,
                    'Name': rd.resource_name,
                    'Number_of_times_accessed__c': rd.number_of_times_accessed,
                    'Last_accessed__c': rd.last_access.strftime('%Y-%m-%d')
                })
                number_created = number_created + 1
                rd.salesforce_id = sf_resource['id']
                rd.save()


        response = self.style.SUCCESS("[SF Resource Download] Created {} of {}. Updated {} of {}.".format(number_created,
                                                                                                          number_to_create,
                                                                                                          number_updated,
                                                                                                          number_to_update))
        self.stdout.write(response)
