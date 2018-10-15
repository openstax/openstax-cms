from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from errata.models import Errata
from social_django.models import UserSocialAuth

class Command(BaseCommand):
    help = "updates Errata records to use account id instead of local account"

    def handle(self, *args, **options):
        print('Total Errata: {}'.format(Errata.objects.all().count()))
        print('Errata with submitted by account id: {}'.format(Errata.objects.filter(submitted_by_account_id__isnull=False).count()))
        user_not_exist = 0
        no_social_auth = 0
        no_submitted_by_user = 0
        to_update = 0
        for errata in Errata.objects.all():
            try:
                user = UserSocialAuth.objects.filter(user=errata.submitted_by)[0]
                if errata.submitted_by:
                    to_update = to_update + 1
                    Errata.objects.select_for_update().filter(id=errata.id).update(submitted_by_account_id=user.uid)
                else:
                    no_submitted_by_user = no_submitted_by_user + 1
            except User.DoesNotExist:
                user_not_exist = user_not_exist + 1
            except IndexError:
                no_social_auth = no_social_auth + 1
                if errata.submitted_by:
                    user = User.objects.get(id=errata.submitted_by.id)
                    print(user.username)

        print('-------------------------------')
        print('Total updated: {}'.format(to_update))
        print("Errata user accounts migrated!")
        print('Total Errata: {}'.format(Errata.objects.all().count()))
        print('No user ID with errata: {}'.format(no_submitted_by_user))
        print('No user found count: {}'.format(user_not_exist))
        print('No social auth: {}'.format(no_social_auth))
        print('Errata with submitted by account id: {}'.format(Errata.objects.filter(submitted_by_account_id__isnull=False).count()))
