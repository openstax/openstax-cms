from django.core.management.base import BaseCommand
from salesforce.models import PartnerReview

class Command(BaseCommand):
    help = "sync review faculty status with accounts"

    # This command should be removed after it is run in production to populate the faculty status of existing reviews.

    def handle(self, *args, **options):
        reviews = PartnerReview.objects.all()

        for review in reviews:
            review.save()
