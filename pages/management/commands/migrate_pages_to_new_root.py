import json
from django.core.management.base import BaseCommand
from pages.models import HomePage, RootPage


class Command(BaseCommand):
    help="Use this to move the pages the currently exist under the home page to the new root. This keeps the homepage under the new root page."

    def handle(self, *args, **options):
        try:
            root = RootPage.objects.first()
        except RootPage.DoesNotExist:
            root = RootPage.objects.create(title="Home", slug="home")

        home = HomePage.objects.first()
        home.copy(to=root, recursive=True, copy_revisions=True, keep_live=True)
        print("All children of the home page have been moved to the new root.")
