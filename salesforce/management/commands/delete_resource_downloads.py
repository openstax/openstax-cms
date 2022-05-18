from django.core.management.base import BaseCommand
from salesforce.models import ResourceDownload
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "delete resource downloads from CMS database that are 7 days old"

    def handle(self, *args, **options):
        delete_from_date = timezone.now() - timedelta(days=7)
        downloads_to_delete = ResourceDownload.objects.filter(created__lte=delete_from_date)
        num_deleted = len(downloads_to_delete)
        downloads_to_delete.delete()
        response = self.style.SUCCESS("{} resource downloads greater than 7 days old deleted from CMS database".format(num_deleted))
        self.stdout.write(response)