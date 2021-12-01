from django.core.management.base import BaseCommand
from salesforce.models import PartnerReview
from oxauth.functions import get_user_info

class Command(BaseCommand):
    help = "sync review faculty status with accounts"

    # This command should be removed after it is run in production to populate the faculty status of existing reviews.

    def handle(self, *args, **options):
        reviews = PartnerReview.objects.all()

        for review in reviews:
            print('***account id: ' + str(review.submitted_by_account_id))
            user = get_user_info(review.submitted_by_account_id)
            print('***user: ' + str(user))
            print('***review faculty status: ' + str(review.user_faculty_status))
            if user:
                if review.user_faculty_status is not user['faculty_status']:
                    print('***updating review: ' + str(user['faculty_status']))
                    review.user_faculty_status = user['faculty_status']
                    review.save()
