from django.core.management.base import BaseCommand
from django.db import transaction
from salesforce.models import PartnerReview
from oxauth.functions import get_user_info

class Command(BaseCommand):
    help = "update partner reviews to store the uuid instead of the id"

    def handle(self, *args, **options):
        reviews = PartnerReview.objects.filter(submitted_by_account_uuid__isnull=True)

        self.stdout.write(self.style.NOTICE("Updating {} records. This might take a while.".format(reviews.count())))

        for review in reviews:
            review.submitted_by_account_uuid = get_user_info(review.submitted_by_account_id)['uuid']
            review.submitted_by_account_id = None
            review.save()

        self.stdout.write(self.style.SUCCESS("Updated UUID fields on {} resource download records.".format(reviews.count())))
