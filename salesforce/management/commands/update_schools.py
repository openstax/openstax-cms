from django.core.management.base import BaseCommand
from salesforce.models import School
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "update schools from salesforce.com"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            query = "SELECT Name, Id, Phone, " \
                      "Website, " \
                      "Type, " \
                      "K_I_P__c, " \
                      "Achieving_the_Dream_School__c, " \
                      "HBCU__c, " \
                      "Texas_Higher_Ed__c, " \
                      "Approximate_Enrollment__c, " \
                      "Pell_Grant_Recipients__c, " \
                      "Students_Pell_Grant__c, " \
                      "Students_Current_Year__c, " \
                      "All_Time_Students2__c, " \
                      "Savings_Current_Year__c, " \
                      "All_Time_Savings2__c, " \
                      "BillingStreet, " \
                      "BillingCity, " \
                      "BillingState, " \
                      "BillingPostalCode, " \
                      "BillingCountry, " \
                      "Address_Latitude__c, " \
                      "Address_Longitude__c," \
                      "Testimonial__c," \
                      "Testimonial_Name__c, " \
                      "Testimonial_Position__c, " \
                      "Number_of_Adoptions__c FROM Account WHERE Number_of_Adoptions__c > 0"
            response = sf.query_all(query)
            sf_schools = response['records']

            district_query = "SELECT Name, Id, Phone, " \
                      "RecordTypeId, " \
                      "Website, " \
                      "Type, " \
                      "K_I_P__c, " \
                      "Achieving_the_Dream_School__c, " \
                      "HBCU__c, " \
                      "Texas_Higher_Ed__c, " \
                      "Approximate_Enrollment__c, " \
                      "Pell_Grant_Recipients__c, " \
                      "Students_Pell_Grant__c, " \
                      "Students_Current_Year__c, " \
                      "All_Time_Students2__c, " \
                      "Savings_Current_Year__c, " \
                      "All_Time_Savings2__c, " \
                      "Adoptions_in_District__c, " \
                      "BillingStreet, " \
                      "BillingCity, " \
                      "BillingState, " \
                      "BillingPostalCode, " \
                      "BillingCountry, " \
                      "Address_Latitude__c, " \
                      "Address_Longitude__c," \
                      "Testimonial__c," \
                      "Testimonial_Name__c, " \
                      "Testimonial_Position__c, " \
                      "Number_of_Adoptions__c FROM Account WHERE RecordTypeId = '012U0000000MdzNIAS' AND K_I_P__c = True"
            district_response = sf.query_all(district_query)
            sf_districts = district_response['records']

            updated_schools = 0
            created_schools = 0
            for sf_district in sf_districts:
                school, created = School.objects.update_or_create(
                        salesforce_id=sf_district['Id'],
                        defaults={'name': sf_district['Name'],
                                  'phone': sf_district['Phone'],
                                  'website': sf_district['Website'],
                                  'type': sf_district['Type'],
                                  'key_institutional_partner': sf_district['K_I_P__c'],
                                  'achieving_the_dream_school': sf_district['Achieving_the_Dream_School__c'],
                                  'hbcu': sf_district['HBCU__c'],
                                  'texas_higher_ed': sf_district['Texas_Higher_Ed__c'],
                                  'undergraduate_enrollment': sf_district['Approximate_Enrollment__c'],
                                  'pell_grant_recipients': sf_district['Pell_Grant_Recipients__c'],
                                  'percent_students_pell_grant': sf_district['Students_Pell_Grant__c'],
                                  'current_year_students': sf_district['Students_Current_Year__c'],
                                  'all_time_students': sf_district['All_Time_Students2__c'],
                                  'current_year_savings': sf_district['Savings_Current_Year__c'],
                                  'all_time_savings': sf_district['All_Time_Savings2__c'],
                                  'physical_country': sf_district['BillingCountry'],
                                  'physical_street': sf_district['BillingStreet'],
                                  'physical_city': sf_district['BillingCity'],
                                  'physical_state_province': sf_district['BillingState'],
                                  'physical_zip_postal_code': sf_district['BillingPostalCode'],
                                  'lat': sf_district['Address_Latitude__c'],
                                  'long': sf_district['Address_Longitude__c'],
                                  'testimonial': sf_district['Testimonial__c'],
                                  'testimonial_name': sf_district['Testimonial_Name__c'],
                                  'testimonial_position': sf_district['Testimonial_Position__c']
                                  },
                    )
                school.save()
                if created:
                    created_schools = created_schools + 1
                else:
                    updated_schools = updated_schools + 1

            for sf_school in sf_schools:
                school, created = School.objects.update_or_create(
                    salesforce_id=sf_school['Id'],
                    defaults={'name': sf_school['Name'],
                              'phone': sf_school['Phone'],
                              'website': sf_school['Website'],
                              'type': sf_school['Type'],
                              'key_institutional_partner': sf_school['K_I_P__c'],
                              'achieving_the_dream_school': sf_school['Achieving_the_Dream_School__c'],
                              'hbcu': sf_school['HBCU__c'],
                              'texas_higher_ed': sf_school['Texas_Higher_Ed__c'],
                              'undergraduate_enrollment': sf_school['Approximate_Enrollment__c'],
                              'pell_grant_recipients': sf_school['Pell_Grant_Recipients__c'],
                              'percent_students_pell_grant': sf_school['Students_Pell_Grant__c'],
                              'current_year_students': sf_school['Students_Current_Year__c'],
                              'all_time_students': sf_school['All_Time_Students2__c'],
                              'current_year_savings': sf_school['Savings_Current_Year__c'],
                              'all_time_savings': sf_school['All_Time_Savings2__c'],
                              'physical_country': sf_school['BillingCountry'],
                              'physical_street': sf_school['BillingStreet'],
                              'physical_city': sf_school['BillingCity'],
                              'physical_state_province': sf_school['BillingState'],
                              'physical_zip_postal_code': sf_school['BillingPostalCode'],
                              'lat': sf_school['Address_Latitude__c'],
                              'long': sf_school['Address_Longitude__c'],
                              'testimonial': sf_school['Testimonial__c'],
                              'testimonial_name': sf_school['Testimonial_Name__c'],
                              'testimonial_position': sf_school['Testimonial_Position__c']
                              },
                )

                school.save()
                if created:
                    created_schools = created_schools + 1
                else:
                    updated_schools = updated_schools + 1

            response = self.style.SUCCESS("Successfully updated {} schools, created {} schools.".format(updated_schools, created_schools))
        self.stdout.write(response)
