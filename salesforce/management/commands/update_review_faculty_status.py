from django.core.management.base import BaseCommand
from salesforce.models import PartnerReview
from oxauth.functions import get_user_info

class Command(BaseCommand):
    help = "sync review faculty status with accounts"

    def handle(self, *args, **options):
        reviews = PartnerReview.objects.all()

        for review in reviews:
            user = get_user_info(review.submitted_by_account_id)
            if user is not False:
                if review.user_faculty_status is not user['faculty_status']:
                    review.user_faculty_status = user['faculty_status']
                    review.save()
