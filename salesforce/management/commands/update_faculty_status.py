from django.core.management.base import BaseCommand, CommandError
from salesforce.salesforce import Salesforce
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = "Add user to faculty group if confirmed by salesforce"

    def add_arguments(self, parser):
        parser.add_argument('cms_id', type=int)
        parser.add_argument('accounts_id', type=int)

    def handle(self, *args, **options):
        with Salesforce() as sf:
            user = User.objects.get(pk=options['cms_id'])
            status = sf.faculty_status(options['accounts_id'])
            if status == u'Confirmed':
                faculty_group = Group.objects.get_by_natural_key('Faculty')
                user.groups.add(faculty_group)
                user.save()
        responce = self.style.SUCCESS("Successfully updated user faculty status")
        self.stdout.write(responce)

