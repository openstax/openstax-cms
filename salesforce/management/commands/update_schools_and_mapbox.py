from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "update schools from salesforce.com and then upload geoJSON school data to Mapbox"

    def handle(self, *args, **options):
        print("Running update_schools...")
        call_command("update_schools")

        print("Running upload_mapbox_schools...")
        call_command("upload_mapbox_schools")
        