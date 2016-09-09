from django.contrib.auth.models import User, Group

from salesforce.salesforce import Salesforce
from social.apps.django_app.default.models import \
    DjangoStorage as SocialAuthStorage


def check_if_faculty_pending(user_id):
    with Salesforce() as sf:
        try:
            social_user = SocialAuthStorage.user.objects.filter(user_id=user_id)
            accounts_id = social_user[0].uid
            command = "SELECT OS_Accounts_ID__c FROM Lead WHERE OS_Accounts_ID__c = '{}'".format(accounts_id)
            response = sf.query(command)

            try:
                record = response['records'][0]['OS_Accounts_ID__c']
                return True
            except IndexError:
                return False
        except IndexError:
            return False


def update_faculty_status(user_id):
    faculty_group, created = Group.objects.get_or_create(name="Faculty")

    with Salesforce() as sf:
        try:
            user = User.objects.get(pk=user_id)
            social_user = SocialAuthStorage.user.objects.filter(user=user)
            accounts_id = social_user[0].uid
            command = "SELECT Accounts_ID__c FROM Contact " \
                      "WHERE Faculty_Verified__c = 'Confirmed' " \
                      "AND Accounts_ID__c = '{}'".format(accounts_id)
            response = sf.query(command)

            try:
                record = response['records'][0]['OS_Accounts_ID__c']
                if record:
                    faculty_group.user_set.add(user)
                    user.save()
                return True
            except IndexError:
                return False
        except IndexError:
            return False