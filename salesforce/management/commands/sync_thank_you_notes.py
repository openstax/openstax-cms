from django.core.management.base import BaseCommand
from salesforce.models import School
from donations.models import ThankYouNote
from salesforce.salesforce import Salesforce
from rapidfuzz import process, fuzz


class Command(BaseCommand):
    help = "update thank you note records with SF"

    def handle(self, *args, **options):
        new_thank_you_notes = ThankYouNote.objects.filter(salesforce_id="")
        print(new_thank_you_notes)

        with Salesforce() as sf:
            # fetch schools to do a fuzzy match on with thank you note manually inputted names
            school_list = {school.name: school.salesforce_id for school in School.objects.all()}

            num_created = 0

            for note in new_thank_you_notes:
                if note.institution:
                    best_match, score, _ = process.extractOne(note.institution, school_list.keys(), scorer=fuzz.WRatio)

                    if score > 80:
                        account_id = school_list[best_match]

                        response = sf.Note.create({'Title': f"{note.created} | {note.first_name} {note.last_name} | {note.contact_email_address} | {note.institution}",
                                                   'Body': f"Consent to share/be contacted? {note.consent_to_share_or_contact}\nSource: {note.source}\n\n{note.thank_you_note}",
                                                   'ParentId': account_id})

                        note.salesforce_id = response['id']
                        note.save()
                        num_created += 1

            self.stdout.write(self.style.SUCCESS("{} Salesforce Notes Created.".format(num_created)))
