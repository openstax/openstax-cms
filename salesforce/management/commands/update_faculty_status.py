from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from salesforce.salesforce import Salesforce
from social.apps.django_app.default.models import \
    DjangoStorage as SocialAuthStorage
import argparse

class Command(BaseCommand):
    help = "Add user to faculty group if confirmed by salesforce"

    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs='?', type=int, default=None)
        parser.add_argument('--all', action='store_true', default=False)

    def handle(self, *args, **options):
        with Salesforce() as sf:
            if options['all']:
                command = "SELECT Accounts_ID__c FROM Contact "\
                              "WHERE Faculty_Verified__c = 'Confirmed' "\
                              "AND Accounts_ID__c != null"
                response = sf.query_all(command)
            elif options['user_id']:
                social_user = SocialAuthStorage.user.objects.filter(
                    user_id=options['user_id'])
                accounts_id = social_user[0].uid
                command = "SELECT Accounts_ID__c FROM Contact "\
                              "WHERE Faculty_Verified__c = 'Confirmed' "\
                              "AND Accounts_ID__c = '{}'".format(accounts_id)
                response = sf.query(command)
            else:
                raise argparse.ArgumentError()
            records = response['records']
            faculty_list = [contact['Accounts_ID__c'] for contact in records]
            for account_id in faculty_list:
                social_user = SocialAuthStorage.user.objects.filter(
                    uid=account_id)
                if social_user:
                    cms_id = social_user[0].user_id
                    user = User.objects.get(pk=cms_id)
                    faculty_group = Group.objects.get_by_natural_key('Faculty')
                    user.groups.add(faculty_group)
                    user.save()
                    faculty_group.save()
        responce = self.style.SUCCESS(
            "Successfully updated user faculty status")
        self.stdout.write(responce)

