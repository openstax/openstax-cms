from django.core.management.base import BaseCommand
from django.db import transaction
from salesforce.models import AdoptionOpportunityRecord
from oxauth.functions import get_user_info

class Command(BaseCommand):
    help = "update adoption opps to store the uuid instead of the id"

    def handle(self, *args, **options):
        adoption_opps = AdoptionOpportunityRecord.objects.filter(account_uuid__isnull=True)

        self.stdout.write(self.style.NOTICE("Updating {} records. This might take a while.".format(adoption_opps.count())))

        for opp in adoption_opps:
            opp.account_uuid = get_user_info(opp.account_id)['uuid']
            opp.account_id = None
            opp.save()

        self.stdout.write(self.style.SUCCESS("Updated UUID fields on {} resource download records.".format(reviews.count())))
