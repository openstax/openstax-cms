from django.core.management.base import BaseCommand
from salesforce.models import School
from donations.models import ThankYouNote
from salesforce.salesforce import Salesforce
from rapidfuzz import process, fuzz


class Command(BaseCommand):
    help = "update thank you note records with SF"

    def handle(self, *args, **options):
        new_thank_you_notes = ThankYouNote.objects.filter(salesforce_id__isnull=True)

        with Salesforce() as sf:
            # fetch schools to do a fuzzy match on with thank you note manually inputted names
            school_list = {school.name: school.salesforce_id for school in School.objects.all()}

            num_created = 0

            for note in new_thank_you_notes:
                if note.institution:
                    best_match, score, _ = process.extractOne(note.institution, school_list.keys(), scorer=fuzz.WRatio)

                    if score < 80:
                        # TODO: log this somewhere better or just ignore it
                        self.stdout.write(self.style.WARNING("No good match for {} (highest match score: {}/{})".format(note.institution, best_match, score)))

                        account_id = school_list[best_match]

                        response = sf.Note.create({'Title': f"{note.created} | {note.first_name} {note.last_name} | {note.contact_email_address} | {note.institution}",
                                                   'Body': f"Consent to share/be contacted? {note.consent_to_share_or_contact}\n\n{note.thank_you_note}",
                                                   'ParentId': account_id})

                    else:  # can't find a school match, just upload as a general note
                        response = sf.Note.create({'Title': f"{note.created} | {note.first_name} {note.last_name} | {note.contact_email_address} | {note.institution}",
                                                   'Body': f"Consent to share/be contacted? {note.consent_to_share_or_contact}\n\n{note.thank_you_note}"})

                    note.salesforce_id = response['id']
                    note.save()
                    num_created += 1

            response = self.style.SUCCESS("{} Salesforce Notes Created.".format(num_created))
            self.stdout.write(response)
