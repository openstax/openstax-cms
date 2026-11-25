from django.core.management.base import BaseCommand

from salesforce.models import SalesforceBookName
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "Sync the Salesforce Book__c list into SalesforceBookName (for the salesforce_name dropdown)."

    def handle(self, *args, **options):
        with Salesforce() as sf:
            response = sf.query_all("Select Id, Name, Official_Name__c from Book__c")
        created = updated = 0
        for record in response['records']:
            obj, was_created = SalesforceBookName.objects.update_or_create(
                salesforce_id=record['Id'],
                defaults={
                    'name': record.get('Name'),
                    'official_name': record.get('Official_Name__c'),
                },
            )
            created += int(was_created)
            updated += int(not was_created)
        self.stdout.write(self.style.SUCCESS(
            f"Synced Book__c names: {created} created, {updated} updated."))
