import csv
import os

from django.core.management.base import BaseCommand

import yaml
from accounts.utils import create_user


class Command(BaseCommand):
    help = "import users from a .yaml or .csv file"

    def add_arguments(self, parser):
        parser.add_argument('file_path')

    def handle(self, *args, **options):
        with open(options['file_path'], 'r') as f:
            filename, file_extension = os.path.splitext(options['file_path'])
            if file_extension == '.yaml':
                user_list = yaml.load(f)
            elif file_extension == '.csv':
                reader = csv.reader(f)
                user_list = [row for row in reader]
                headers = user_list.pop(0)
                user_dict_list = []
                for i in range(0, len(user_list)):
                    user_dict = {}
                    for j in range(0, len(headers)):
                        user_dict.update({headers[j]: user_list[i][j]})
                    user_dict_list.append(user_dict)
                user_list = user_dict_list
            else:
                raise NotImplementedError(
                    "'{0}' file type not supported".format(file_extension))
            for accounts_user in user_list:
                new_user_details = {'last_name': accounts_user['last_name'],
                                    'username': accounts_user['username'],
                                    'full_name': None,
                                    'first_name': accounts_user['first_name'],
                                    'uid': accounts_user['id']}
                create_user(**new_user_details)
            response = self.style.SUCCESS("Import Successful")
        self.stdout.write(response)

