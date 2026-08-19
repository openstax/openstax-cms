from django.core.management.base import BaseCommand
from salesforce.models import ResourceDownload
from salesforce.salesforce import Salesforce
from django.utils import timezone
from datetime import timedelta


# Student__c.Name holds the account uuid, which is the only key the two sides
# share. Accounts creates those records, so a download can easily arrive before
# the student it belongs to; an unmatched row still carries Accounts_UUID__c and
# can be matched later.
STUDENT_LOOKUP_CHUNK = 200


def student_ids_by_uuid(sf, account_uuids):
    wanted = sorted({str(uuid) for uuid in account_uuids if uuid})
    found = {}

    for start in range(0, len(wanted), STUDENT_LOOKUP_CHUNK):
        chunk = wanted[start:start + STUDENT_LOOKUP_CHUNK]
        quoted = ', '.join("'{}'".format(uuid) for uuid in chunk)
        results = sf.query_all("SELECT Id, Name FROM Student__c WHERE Name IN ({})".format(quoted))
        for record in results['records']:
            found.setdefault(record['Name'], record['Id'])

    return found


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
            students = student_ids_by_uuid(
                sf, [nrd.account_uuid for nrd in new_resource_downloads if nrd.book])
            new_data = []
            matched_students = 0
            for nrd in new_resource_downloads:
                if nrd.book:
                    student_id = students.get(str(nrd.account_uuid))
                    if student_id:
                        matched_students += 1
                    data_dict_item = {'Contact__c': nrd.contact_id,
                                      'Student__c': student_id,
                                      'Last_accessed__c': nrd.last_access.strftime('%Y-%m-%d'),
                                      'Name': nrd.resource_name,
                                      'Book__c': nrd.book.salesforce_abbreviation,
                                      'Book_Format__c': nrd.book_format,
                                      'Source__c': nrd.source,
                                      'Accounts_UUID__c': str(nrd.account_uuid)}
                    new_data.append(data_dict_item)

            if len(new_data) > 0:
                sf.bulk.Resource__c.insert(new_data)

            self.stdout.write(self.style.SUCCESS(
                "SF Resource Download Completed. Sent: {}. Matched to a student: {}.".format(
                    len(new_data), matched_students)))
