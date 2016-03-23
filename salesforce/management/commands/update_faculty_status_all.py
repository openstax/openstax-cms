from django.core.management.base import BaseCommand
from salesforce.salesforce import Salesforce
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import User, Group
from social.apps.django_app.default.models import DjangoStorage as SocialAuthStorage


class Command(BaseCommand):
    help = "Add user to faculty group if confirmed by salesforce for all users"

    def handle(self, *args, **options):
        SocialAuthStorage.user.objects.all()
        with Salesforce() as sf:
            contact_list = sf.faculty_status()
            for contact in contact_list:
                account_id = contact['Accounts_ID__c']
                social_user = SocialAuthStorage.user.objects.filter(
                    uid=account_id)
                if social_user:
                    user = User.objects.get(pk=social_user[0].user_id)
                    faculty_group = Group.objects.get_by_natural_key('Faculty')
                    user.groups.add(faculty_group)
                    user.save()
                    faculty_group.save()
        responce = self.style.SUCCESS("Successfully updated adopters")
        self.stdout.write(responce)

