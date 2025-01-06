from django.core.management.base import BaseCommand

from global_settings.functions import invalidate_cloudfront_caches
from salesforce.models import School
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "update schools from salesforce.com"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            query = "SELECT Name, Id, Phone, " \
                      "Website, " \
                      "Type, " \
                      "School_Location__c, " \
                      "Approximate_Enrollment__c, " \
                      "Students_Current_Year__c, " \
                      "Total_School_Enrollment__c, " \
                      "BillingStreet, " \
                      "BillingCity, " \
                      "BillingState, " \
                      "BillingPostalCode, " \
                      "BillingCountry, " \
                      "Address_Latitude__c, " \
                      "Address_Longitude_del__c " \
                      "FROM Account"
            response = sf.query_all(query)
            sf_schools = response['records']

            district_query = "SELECT Name, Id, Phone, " \
                      "RecordTypeId, " \
                      "Website, " \
                      "Type, " \
                      "School_Location__c, " \
                      "Approximate_Enrollment__c, " \
                      "Students_Current_Year__c, " \
                      "Total_School_Enrollment__c, " \
                      "Adoptions_in_District__c, " \
                      "BillingStreet, " \
                      "BillingCity, " \
                      "BillingState, " \
                      "BillingPostalCode, " \
                      "BillingCountry, " \
                      "Address_Latitude__c, " \
                      "Address_Longitude_del__c " \
                      "FROM Account WHERE RecordTypeId = '012U0000000MdzNIAS'"
            district_response = sf.query_all(district_query)
            sf_districts = district_response['records']
            #remove duplicates
            sf_schools_to_update = [x for x in sf_schools if x not in sf_districts]

            updated_schools = 0
            created_schools = 0
            for sf_district in sf_districts:
                school, created = School.objects.update_or_create(
                        salesforce_id=sf_district['Id'],
                        defaults={'name': sf_district['Name'],
                                  'phone': sf_district['Phone'],
                                  'website': sf_district['Website'],
                                  'type': sf_district['Type'],
                                  'location': sf_district['School_Location__c'],
                                  'undergraduate_enrollment': sf_district['Approximate_Enrollment__c'],
                                  'current_year_students': sf_district['Students_Current_Year__c'],
                                  'total_school_enrollment': sf_district['Total_School_Enrollment__c'],
                                  'physical_country': sf_district['BillingCountry'],
                                  'physical_street': sf_district['BillingStreet'],
                                  'physical_city': sf_district['BillingCity'],
                                  'physical_state_province': sf_district['BillingState'],
                                  'physical_zip_postal_code': sf_district['BillingPostalCode'],
                                  'lat': sf_district['Address_Latitude__c'],
                                  'long': sf_district['Address_Longitude_del__c'],
                                  },
                    )
                school.save()
                if created:
                    created_schools = created_schools + 1
                else:
                    updated_schools = updated_schools + 1

            for sf_school in sf_schools_to_update:
                school, created = School.objects.update_or_create(
                    salesforce_id=sf_school['Id'],
                    defaults={'name': sf_school['Name'],
                              'phone': sf_school['Phone'],
                              'website': sf_school['Website'],
                              'type': sf_school['Type'],
                              'location': sf_school['School_Location__c'],
                              'undergraduate_enrollment': sf_school['Approximate_Enrollment__c'],
                              'current_year_students': sf_school['Students_Current_Year__c'],
                              'total_school_enrollment': sf_school['Total_School_Enrollment__c'],
                              'physical_country': sf_school['BillingCountry'],
                              'physical_street': sf_school['BillingStreet'],
                              'physical_city': sf_school['BillingCity'],
                              'physical_state_province': sf_school['BillingState'],
                              'physical_zip_postal_code': sf_school['BillingPostalCode'],
                              'lat': sf_school['Address_Latitude__c'],
                              'long': sf_school['Address_Longitude_del__c'],
                              },
                )

                school.save()
                if created:
                    created_schools = created_schools + 1
                else:
                    updated_schools = updated_schools + 1

            invalidate_cloudfront_caches('salesforce/schools')
            response = self.style.SUCCESS("Successfully updated {} schools, created {} schools.".format(updated_schools, created_schools))
        self.stdout.write(response)
