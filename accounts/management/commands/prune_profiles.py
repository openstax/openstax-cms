from django.core.management.base import BaseCommand
from social_django.models import UserSocialAuth
from accounts.models import Profile

class Command(BaseCommand):
    help = "removes all social profiles, which get recreated on login - this should be run during a migration of data (QA->dev for example)"

    def handle(self, *args, **options):
        number_of_auths = UserSocialAuth.objects.count()
        UserSocialAuth.objects.all().delete()
        print('Successfully removed {} social auth profiles.'.format(number_of_auths))

        number_of_profiles = Profile.objects.count()
        Profile.objects.all().delete()
        print('Successfully removed {} local profiles.'.format(number_of_profiles))

        print("These numbers just tell you the script worked. It's fine if they don't match.")
