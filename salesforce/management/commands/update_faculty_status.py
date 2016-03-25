from django.core.management.base import BaseCommand, CommandError
from salesforce.salesforce import Salesforce
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import User, Group
from social.apps.django_app.default.models import DjangoStorage as SocialAuthStorage

class Command(BaseCommand):
    help = "Add user to faculty group if confirmed by salesforce"

    def add_arguments(self, parser):
        parser.add_argument('cms_id', nargs='?', type=int,default=None)
        parser.add_argument('--all', action='store_true', default=False)
    def handle(self, *args, **options):
        if options['all']:
            users = SocialAuthStorage.user.objects.all()
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

        else:
            social_user = SocialAuthStorage.user.objects.filter(user_id = options['cms_id'])
            if social_user:
                with Salesforce() as sf:
                    accounts_id=social_user[0].uid
                    cms_id = social_user[0].user_id
                    status = sf.faculty_status(accounts_id)
                    if status == u'Confirmed':
                        user=User.objects.get(pk = cms_id)
                        faculty_group = Group.objects.get_by_natural_key('Faculty')
                        user.groups.add(faculty_group)
                        user.save()
        responce = self.style.SUCCESS("Successfully updated user faculty status")
        self.stdout.write(responce)

