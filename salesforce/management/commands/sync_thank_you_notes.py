from django.core.management.base import BaseCommand
from salesforce.models import School
from donations.models import ThankYouNote
from salesforce.salesforce import Salesforce
from rapidfuzz import process, fuzz, utils


class Command(BaseCommand):
    help = "update thank you note records with SF"

    def handle(self, *args, **options):
        new_thank_you_notes = ThankYouNote.objects.filter(salesforce_id="")

        with Salesforce() as sf:
            # fetch schools to do a fuzzy match on with thank you note manually inputted names
            school_list = {school.name: school.salesforce_id for school in School.objects.all()}

            num_created = 0
            for note in new_thank_you_notes:
                if note.institution:
                    best_match, score, _ = process.extractOne(note.institution, school_list.keys(), scorer=fuzz.WRatio, processor=utils.default_process)

                    account_id = school_list["Find Me A Home"]
                    if score > 90:  # found a good match on school name, use that to populate related school in SF
                        account_id = school_list[best_match]

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

            self.stdout.write(self.style.SUCCESS("{} Salesforce Notes Created.".format(num_created)))
