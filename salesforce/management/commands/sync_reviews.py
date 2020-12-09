from django.core.management.base import BaseCommand
from salesforce.models import PartnerReview
from salesforce.salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceGeneralError
from global_settings.functions import invalidate_cloudfront_caches

class Command(BaseCommand):
    help = "sync reviews with salesforce"

    def handle(self, *args, **options):
        with Salesforce() as sf:

            # To update the existing reviews with Partner responses and approved reviews.
            command = "Select Id, Status__c, Approved_Customer_Review__c, Pending_Customer_Review__c, Partner_Response__c, Partner_Response_Date__c, Partner__c, Contact__c, Score__c, OS_Accounts_ID__c FROM Partner_Review__c WHERE Status__c = 'Approved' OR Status__c = 'Responded'"
            response = sf.query_all(command)
            sf_reviews = response['records']

            for record in sf_reviews:
                try:
                    review = PartnerReview.objects.get(review_salesforce_id=record['Id'])
                    if review.status != 'Edited':
                        review.review = record['Approved_Customer_Review__c']
                        review.partner_response = record['Partner_Response__c']
                        review.partner_response_date = record['Partner_Response_Date__c']
                        review.status = 'Approved'
                        review.save()
                except PartnerReview.DoesNotExist:
                    print('Review does not exist for SF ID: {}'.format(record['Id']))

            # Update rejected reviews
            command = "Select Id, Status__c, Approved_Customer_Review__c, Pending_Customer_Review__c, Partner_Response__c, Partner_Response_Date__c, Partner__c, Contact__c, Score__c, OS_Accounts_ID__c FROM Partner_Review__c WHERE Status__c = 'Rejected'"
            response = sf.query_all(command)
            sf_reviews = response['records']

            for record in sf_reviews:
                try:
                    review = PartnerReview.objects.get(review_salesforce_id=record['Id'])
                    review.status = 'Rejected'
                    review.save()
                except PartnerReview.DoesNotExist:
                    print('Review does not exist for SF ID: {}'.format(record['Id']))


            # If a review does not have a Salesforce ID, it must be new. We'll upload those to SF and assign a SF ID.
            new_reviews = PartnerReview.objects.filter(review_salesforce_id__isnull=True)
            for review in new_reviews:
                data = {
                    'Status__c': 'New',
                    'Pending_Customer_Review__c': review.review,
                    'Partner__c': review.partner.salesforce_id,
                    'OS_Accounts_ID__c': review.submitted_by_account_id,
                    'Score__c': review.rating,
                }
                try:
                    response = sf.Partner_Review__c.create(data)
                    review.review_salesforce_id = response['id']
                    review.save()
                except SalesforceGeneralError:
                    print('Failed to create review in Salesforce - are you sure the partner exists?')



            # If a review is in the Edited state, it needs to be reuploaded to SF and set to 'New'
            update_reviews = PartnerReview.objects.filter(status='Edited')
            for review in update_reviews:
                data = {
                    'Status__c': 'New',
                    'Pending_Customer_Review__c': review.review,
                    'OS_Accounts_ID__c': review.submitted_by_account_id,
                    'Score__c': review.rating,
                }
                try:
                    response = sf.Partner_Review__c.update(data=data, record_id=review.review_salesforce_id)
                    review.status = 'Awaiting Approval'
                    review.save()
                except SalesforceGeneralError:
                    print('Failed to update review in Salesforce')

            # Finally, if a review was deleted by a user, let's delete it from Salesforce.
            reviews_to_delete = PartnerReview.objects.filter(status='Deleted')
            for review in reviews_to_delete:
                if review.review_salesforce_id:
                    sf.Partner_Review__c.delete(review.review_salesforce_id)
                review.delete()


            invalidate_cloudfront_caches()
            response = self.style.SUCCESS("Successfully updated partner reviews")
        self.stdout.write(response)
