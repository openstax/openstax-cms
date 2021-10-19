from django.core.management.base import BaseCommand
from django.db import transaction
from salesforce.models import ResourceDownload
from oxauth.functions import get_user_info

class Command(BaseCommand):
    help = "update resource download to store the uuid instead of the id"

    def handle(self, *args, **options):
        resource_downloads = ResourceDownload.objects.filter(account_uuid__isnull=True)

        self.stdout.write(self.style.NOTICE("Updating {} records. This might take awhile.".format(resource_downloads.count())))

        for rd in resource_downloads:
            rd.account_uuid = get_user_info(rd.account_id)['uuid']
            rd.account_id =None
            rd.save()

        self.stdout.write(self.style.SUCCESS("Updated UUID fields on {} resource download records.".format(resource_downloads.count())))
