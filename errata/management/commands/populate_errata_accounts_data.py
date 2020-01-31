from django.core.management.base import BaseCommand
from errata.models import Errata
from oxauth.functions import get_user_info

class Command(BaseCommand):
    help = "updates Errata records to populate user info from accounts, avoiding calls to accounts API during export"

    def handle(self, *args, **options):
        print('Total Errata: {}'.format(Errata.objects.all().count()))
        updated_errata = 0
        no_user = 0

        for errata in Errata.objects.all():
            try:
                user = get_user_info(errata.submitted_by_account_id)
                if user:
                    errata.accounts_user_email = user['email']
                    errata.accounts_user_name = user['fullname']
                    errata.accounts_user_faculty_status = user['faculty_status']
                    errata.save()
                    updated_errata = updated_errata + 1
                else:
                    no_user = no_user + 1
            except Exception as e:
                print(e)
                break

        print('Updated Errata Count: {}'.format(updated_errata))
        print('No User Found Count: {}'.format(no_user))
