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
                                "Industry, " \
                                "School_Location__c, " \
                                "Students_Current_Year__c, " \
                                "Total_School_Enrollment__c, " \
                                "BillingStreet, " \
                                "BillingCity, " \
                                "BillingState, " \
                                "BillingPostalCode, " \
                                "BillingCountry, " \
                                "BillingLatitude, " \
                                "BillingLongitude, " \
                                "Research_Agreement_Start_Date__c, " \
                                "Research_Agreement_End_Date__c " \
                                "FROM Account WHERE Industry = 'HE' OR Industry = 'K12'", lazy_operation=True)
            sf_schools = []
            for list_results in fetch_results:
                sf_schools.extend(list_results)

            updated_schools = 0
            created_schools = 0
            seen_salesforce_ids = set()

            for sf_school in sf_schools:
                salesforce_id = sf_school['Id']
                seen_salesforce_ids.add(salesforce_id)
                
                school, created = School.objects.update_or_create(
                    salesforce_id=salesforce_id,
                    defaults={'name': sf_school['Name'],
                              'phone': sf_school['Phone'],
                              'website': sf_school['Website'],
                              'type': sf_school['Type'],
                              'industry': sf_school['Industry'],
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
                              'research_agreement_start_date': sf_school['Research_Agreement_Start_Date__c'],
                              'research_agreement_end_date': sf_school['Research_Agreement_End_Date__c'],
                              },
                )

                if created:
                    created_schools = created_schools + 1
                else:
                    updated_schools = updated_schools + 1

            # Delete schools that no longer exist in Salesforce
            deleted_schools = School.objects.exclude(
                salesforce_id__in=seen_salesforce_ids
            ).delete()[0]

            invalidate_cloudfront_caches('salesforce/schools')
            response = self.style.SUCCESS(
                "Successfully updated {} schools, created {} schools, deleted {} schools.".format(
                    updated_schools, created_schools, deleted_schools))
        self.stdout.write(response)
