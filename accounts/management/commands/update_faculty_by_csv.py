import csv
import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


class Command(BaseCommand):
    help = "update user accounts from a .csv file containing faculty profiles"

    def add_arguments(self, parser):
        parser.add_argument('file_path')

    def handle(self, *args, **options):
        faculty_group, created = Group.objects.get_or_create(name="Faculty")

        with open(options['file_path'], 'r') as f:
            filename, file_extension = os.path.splitext(options['file_path'])
            if file_extension == '.csv':
                reader = csv.reader(f)
                faculty_list = [row for row in reader]
                headers = faculty_list.pop(0)
                for faculty_member in faculty_list:
                    first_name = faculty_member[0]
                    last_name = faculty_member[1]

                    try:
                        user = User.objects.get(first_name=first_name, last_name=last_name)
                        faculty_group.user_set.add(user)
                        print("{} {} added to faculty group.".format(first_name, last_name))
                    except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
                        print("error finding user {} {} - ({})".format(first_name, last_name, e))

            else:
                raise NotImplementedError(
                    "'{0}' file type not supported".format(file_extension))
