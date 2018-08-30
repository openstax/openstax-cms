from django.core.management.base import BaseCommand
from errata.models import Errata


class Command(BaseCommand):
    help = "updates Errata records to use book name in a text field"

    def handle(self, *args, **options):
        for errata in Errata.objects.all():
            Errata.objects.select_for_update().filter(id=errata.id).update(openstax_book=errata.book.title)

        print("Errata books migrated!")
