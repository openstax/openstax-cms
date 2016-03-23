from django.core.management.base import BaseCommand, CommandError
from accounts.utils import create_user
import yaml


class Command(BaseCommand):
    help = "import users from a .yaml file"

    def add_arguments(self, parser):
        parser.add_argument('file_path')

    def handle(self, *args, **options):
        with open(options['file_path'], 'r') as f:
            user_list = yaml.load(f)
            for accounts_user in user_list:
                new_user_details = {'last_name': accounts_user['last_name'],
                                    'username': accounts_user['username'],
                                    'full_name': None,
                                    'first_name': accounts_user['first_name'],
                                    'uid': accounts_user['id']}
                create_user(**new_user_details)
            responce = self.style.SUCCESS("Successfully updated adopters")
        self.stdout.write(responce)

