from django.core.management.base import BaseCommand
from salesforce.models import School
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "update schhols from salesforce.com"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            command = "SELECT Name FROM Account"
            response = sf.query_all(command)
            sf_schools = response['records']

            if sf_schools:
                School.objects.all().delete()

            for sf_school in sf_schools:

                school, created = School.objects.update_or_create(name=sf_school['Name'])

                school.save()
            response = self.style.SUCCESS("Successfully updated schools")
        self.stdout.write(response)
