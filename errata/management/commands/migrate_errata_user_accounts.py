from django.core.management.base import BaseCommand
from errata.models import Errata
from social_django.models import UserSocialAuth

class Command(BaseCommand):
    help = "updates Errata records to use account id instead of local account"

    def handle(self, *args, **options):
        for errata in Errata.objects.all():
            try:
                user = UserSocialAuth.objects.filter(user=errata.submitted_by)[0]
                Errata.objects.select_for_update().filter(id=errata.id).update(submitted_by_account_id=user.uid)
            except IndexError:
                print("No user found for errata with id of {} (user = {})".format(errata.id, errata.submitted_by))

        print("Errata user accounts migrated!")
