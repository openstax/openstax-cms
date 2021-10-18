from django.core.management.base import BaseCommand
from django.db import transaction
from salesforce.models import ResourceDownload
from oxauth.functions import get_user_info

class Command(BaseCommand):
    help = "update resource download to store the uuid instead of the id"

    def handle(self, *args, **options):
        resource_downloads = ResourceDownload.objects.all()

        for rd in resource_downloads:
            if not rd.account_uuid:
                rd.account_uuid = get_user_info(rd.account_id)['account_uuid']
                rd.account_id =None
                rd.save()

        response = self.style.SUCCESS("[SF Resource Download] Updated UUID fields on resource download records.".format(num_updated, num_failed))
        self.stdout.write(response)
