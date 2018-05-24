from django.core.management.base import BaseCommand
from salesforce.models import School
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "update schools from salesforce.com"

    def handle(self, *args, **options):
        with Salesforce() as sf:
            query = "SELECT Name, Phone, " \
                      "Website, " \
                      "Type, " \
                      "K_I_P__c, " \
                      "Achieving_the_Dream_School__c, " \
                      "HBCU__c, " \
                      "Texas_Higher_Ed__c, " \
                      "Approximate_Enrollment__c, " \
                      "Pell_Grant_Recipients__c, " \
                      "Students_Pell_Grant__c, " \
                      "Current_Students__c, " \
                      "All_Time_Students2__c, " \
                      "Current_Savings__c, " \
                      "All_Time_Savings2__c, " \
                      "BillingStreet, " \
                      "BillingCity, " \
                      "BillingState, " \
                      "BillingPostalCode, " \
                      "BillingCountry, " \
                      "Location__c, " \
                      "Testimonial__c  FROM Account"
            response = sf.query_all(query)
            sf_schools = response['records']

            if sf_schools:
                School.objects.all().delete()

            for sf_school in sf_schools:

                #TODO: get location data using sf_school['Location__c'], it's a geolocation field in SF, so not sure what it'll return until there is some data in SF.
                school, created = School.objects.update_or_create(name=sf_school['Name'],
                                                                  phone=sf_school['Phone'],
                                                                  website=sf_school['Website'],
                                                                  type=sf_school['Type'],
                                                                  #adoption_date=sf_school[''],
                                                                  key_institutional_partner=sf_school['K_I_P__c'],
                                                                  achieving_the_dream_school=sf_school['Achieving_the_Dream_School__c'],
                                                                  hbcu=sf_school['HBCU__c'],
                                                                  texas_higher_ed=sf_school['Texas_Higher_Ed__c'],
                                                                  undergraduate_enrollment=sf_school['Approximate_Enrollment__c'],
                                                                  pell_grant_recipients=sf_school['Pell_Grant_Recipients__c'],
                                                                  percent_students_pell_grant=sf_school['Students_Pell_Grant__c'],
                                                                  current_year_students=sf_school['Current_Students__c'],
                                                                  all_time_students=sf_school['All_Time_Students2__c'],
                                                                  current_year_savings=sf_school['Current_Savings__c'],
                                                                  all_time_savings=sf_school['All_Time_Savings2__c'],
                                                                  physical_country=sf_school['BillingCountry'],
                                                                  physical_street=sf_school['BillingStreet'],
                                                                  physical_city=sf_school['BillingCity'],
                                                                  physical_state_province=sf_school['BillingState'],
                                                                  physical_zip_postal_code=sf_school['BillingPostalCode'],
                                                                  #long=sf_school[''], #TODO: parse out location data and save as long, lat decimal forms
                                                                  #lat=sf_school[''],
                                                                  testimonial=sf_school['Testimonial__c'])

                print(school)
                school.save()
            response = self.style.SUCCESS("Successfully updated schools")
        self.stdout.write(response)
