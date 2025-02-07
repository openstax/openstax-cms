from sentry_sdk import capture_exception
from django.core.management.base import BaseCommand
from salesforce.models import School
from donations.models import ThankYouNote
from salesforce.salesforce import Salesforce
from rapidfuzz import process, fuzz, utils
from simple_salesforce.exceptions import SalesforceMalformedRequest


class Command(BaseCommand):
    help = "update thank you note records with SF"

    def handle(self, *args, **options):
        new_thank_you_notes = ThankYouNote.objects.filter(salesforce_id="")

        # fetch schools to do a fuzzy match on with thank you note manually inputted names
        school_list = {school.name: school.salesforce_id for school in School.objects.all()}

        with Salesforce() as sf:
            num_created = 0
            for note in new_thank_you_notes:
                # junk removal
                if note.thank_you_note and len(note.thank_you_note) < 5:  # we expect at least a 'thank'
                    note.delete()
                # junk school rename
                if note.institution and note.institution.isdigit():  # we expect at least text
                    note.institution = "Find Me A Home"  # Use Find Me A Home
                    note.save()


                account_id = school_list["Find Me A Home"]

                # If note has a school name, see if we can match it and use that account id when creating
                if note.institution:
                    school_string = note.institution
                    filtered_choices = [name for name in school_list.keys() if name.lower().startswith(school_string.lower())]
                    if filtered_choices:
                        best_match, score, match_key = process.extractOne(school_string, filtered_choices, scorer=fuzz.partial_ratio, processor=utils.default_process)

                        if score > 99:  # found a good match on school name, use that to populate related school in SF
                            account_id = school_list[best_match]
                        else:
                            capture_exception(Exception(f"Could not find a match for {school_string}"))
                            account_id = school_list["Find Me A Home"]

                try:
                    response = sf.Thank_You_Note__c.create(
                        {'Name': f"{note.first_name} {note.last_name} - {note.created}",
                         'Message__c': note.thank_you_note,
                         'First_Name__c': note.first_name,
                         'Last_Name__c': note.last_name,
                         'Email_Address__c': note.contact_email_address,
                         'Institution__c': note.institution,
                         'Source__c': note.source,
                         'Consent_to_Share__c': note.consent_to_share_or_contact,
                         'Submitted_Date__c': note.created.strftime('%Y-%m-%d'),
                         'Related_Account__c': account_id
                         }
                    )

                    note.salesforce_id = response['id']
                    note.save()
                    num_created += 1
                except SalesforceMalformedRequest as e:
                    capture_exception(e)

            self.stdout.write(self.style.SUCCESS("{} Salesforce Notes Created.".format(num_created)))
