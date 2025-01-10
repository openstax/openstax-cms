from django.core.management.base import BaseCommand

from global_settings.functions import invalidate_cloudfront_caches
from salesforce.models import School
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "update schools from salesforce.com"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            fetch_results = sf.bulk.Account.query("SELECT Name, Id, Phone, " \
                                "Website, " \
                                "Type, " \
                                "School_Location__c, " \
                                "Students_Current_Year__c, " \
                                "Total_School_Enrollment__c, " \
                                "BillingStreet, " \
                                "BillingCity, " \
                                "BillingState, " \
                                "BillingPostalCode, " \
                                "BillingCountry, " \
                                "BillingLatitude, " \
                                "BillingLongitude " \
                                "FROM Account", lazy_operation=True)
            sf_schools = []
            for list_results in fetch_results:
                sf_schools.extend(list_results)

            updated_schools = 0
            created_schools = 0

            for sf_school in sf_schools:
                school, created = School.objects.update_or_create(
                    salesforce_id=sf_school['Id'],
                    defaults={'name': sf_school['Name'],
                              'phone': sf_school['Phone'],
                              'website': sf_school['Website'],
                              'type': sf_school['Type'],
                              'location': sf_school['School_Location__c'],
                              'current_year_students': sf_school['Students_Current_Year__c'],
                              'total_school_enrollment': sf_school['Total_School_Enrollment__c'],
                              'physical_country': sf_school['BillingCountry'],
                              'physical_street': sf_school['BillingStreet'],
                              'physical_city': sf_school['BillingCity'],
                              'physical_state_province': sf_school['BillingState'],
                              'physical_zip_postal_code': sf_school['BillingPostalCode'],
                              'lat': sf_school['BillingLatitude'],
                              'long': sf_school['BillingLongitude'],
                              },
                )

                school.save()
                if created:
                    created_schools = created_schools + 1
                else:
                    updated_schools = updated_schools + 1

            invalidate_cloudfront_caches('salesforce/schools')
            response = self.style.SUCCESS(
                "Successfully updated {} schools, created {} schools.".format(updated_schools, created_schools))
        self.stdout.write(response)
